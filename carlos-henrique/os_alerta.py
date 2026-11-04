#!/usr/bin/env python3
"""Alerta de prazo das O.S. do IXC (SOMENTE LEITURA). Arquivo único, só biblioteca padrão do Python.

Uso:
  Visão de gerente (Dona Socorro): os_alerta.py --modo gerente --tecnicos 140,121,161
  Aviso pessoal do técnico:        os_alerta.py --modo pessoal --tecnico 140 --so-dias-uteis
  Dados em JSON (para o agente):   acrescente --json

Variáveis de ambiente:
  IXC_TOKEN     token do IXC no formato id:hash (obrigatório; NUNCA passe por argumento nem imprima)
  IXC_BASE_URL  padrão https://gestorixc.webfoco.net/webservice/v1

Regras (confirmadas com o Henrique em 03/11/2026):
  aberta  = status diferente de "F"
  pausada = id_assunto 278 (Pausado/Congelado)
  alerta  = aberta há mais de 48 h desde data_abertura, exceto pausadas (horário de Brasília)
  grupos  = 🔴 mais de 30 dias | 🟠 7 a 30 dias | 🟡 48 h a 7 dias

Não imprime dado de cliente: só id da O.S., assunto, idade e se foi assumida.
Se não houver nada a avisar, não imprime NADA e sai com código 0: o agente não deve enviar mensagem.
Erros vão para o stderr com código 1 (a mensagem nunca contém o token).
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BASE_URL_PADRAO = "https://gestorixc.webfoco.net/webservice/v1"
FUSO = ZoneInfo("America/Sao_Paulo")
STATUS_FECHADAS = {"F"}
ASSUNTO_PAUSADO = "278"
ALERTA_H, ATENCAO_H, CRITICA_H = 48, 168, 720
MAX_PAGINAS = 20
LIMITE_TELEGRAM = 3800

TECNICOS = {140: "Milena", 121: "Luiz Felipe", 161: "Edson", 118: "Carlos Henrique", 139: "Raissa", 144: "Paloma", 24: "Socorro", 176: "Bruna"}
ASSUNTOS = {
    "5": "Ativação de cliente",
    "20": "Vistoria Interna",
    "56": "Ativação",
    "74": "Alteração de Endereço",
    "212": "Criação de PPI",
    "235": "Mudança de Titularidade",
    "256": "Registro de Tratativa",
    "278": "Pausado/Congelado",
}
GRUPOS = (
    ("criticas", "🔴 Mais de 30 dias"),
    ("atencao", "🟠 De 7 a 30 dias"),
    ("recentes", "🟡 De 48 h a 7 dias"),
    ("pausadas", "⏸ Pausadas"),
)


class ErroIxc(RuntimeError):
    pass


class Ixc:
    def __init__(self, token: str, base_url: str = BASE_URL_PADRAO, timeout: float = 30.0):
        auth = base64.b64encode(token.encode()).decode()
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json", "ixcsoft": "listar"}
        self.timeout = timeout

    def listar(self, tabela: str, campo: str, valor: str, page: int = 1, rp: int = 30, ordenar_id_desc: bool = False) -> list[dict]:
        corpo = {"qtype": f"{tabela}.{campo}", "query": str(valor), "oper": "=", "page": str(page), "rp": str(rp)}
        if ordenar_id_desc:
            corpo.update({"sortname": f"{tabela}.id", "sortorder": "desc"})
        req = urllib.request.Request(f"{self.base_url}/{tabela}", data=json.dumps(corpo).encode(), headers=self.headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                dados = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise ErroIxc(f"IXC respondeu {e.code}") from None
        except (urllib.error.URLError, TimeoutError, ValueError):
            raise ErroIxc("falha de rede ou resposta inválida do IXC") from None
        if isinstance(dados, dict) and dados.get("type") == "error":
            raise ErroIxc(str(dados.get("message", "erro do IXC"))[:200])
        return (dados.get("registros") if isinstance(dados, dict) else None) or []


def parse_dt(valor):
    if not valor or str(valor).startswith("0000"):
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(valor), fmt)
        except ValueError:
            pass
    return None


def os_abertas(ixc: Ixc, tecnico_id: int) -> list[dict]:
    """Mais recentes primeiro; teto de 20 páginas (600 O.S.). Só os campos necessários."""
    regs: list[dict] = []
    for pagina in range(1, MAX_PAGINAS + 1):
        lote = ixc.listar("su_oss_chamado", "id_tecnico", str(tecnico_id), page=pagina, ordenar_id_desc=True)
        regs += lote
        if len(lote) < 30:
            break
    campos = ("id", "id_assunto", "data_abertura", "data_hora_assumido", "status")
    return [{c: r.get(c) for c in campos} for r in regs if r.get("status") not in STATUS_FECHADAS]


def completar_assuntos(ixc: Ixc, ids) -> None:
    for i in {str(x) for x in ids if x not in (None, "")} - set(ASSUNTOS):
        try:
            regs = ixc.listar("su_oss_assunto", "id", i, rp=1)
        except ErroIxc:
            continue
        nome = str(regs[0].get("assunto", "")).strip() if regs else ""
        if nome:
            ASSUNTOS[i] = nome


def classificar(abertas: list[dict], agora: datetime) -> dict[str, list[dict]]:
    """Exatamente 48 h ainda não é alerta; 168 h e 720 h ficam em 'atenção'. Pausadas ficam fora do alerta."""
    grupos = {k: [] for k, _ in GRUPOS}
    for r in abertas:
        abertura = parse_dt(r.get("data_abertura"))
        idade = agora - abertura if abertura else timedelta(0)
        horas = max(0, int(idade.total_seconds() // 3600))
        item = {**r, "horas": horas, "dias": horas // 24, "assumida": parse_dt(r.get("data_hora_assumido")) is not None}
        if str(r.get("id_assunto")) == ASSUNTO_PAUSADO:
            grupo = "pausadas"
        elif abertura is None or idade <= timedelta(hours=ALERTA_H):
            continue
        elif idade > timedelta(hours=CRITICA_H):
            grupo = "criticas"
        elif idade >= timedelta(hours=ATENCAO_H):
            grupo = "atencao"
        else:
            grupo = "recentes"
        grupos[grupo].append(item)
    for lista in grupos.values():
        lista.sort(key=lambda x: parse_dt(x.get("data_abertura")) or datetime.max)
    return grupos


def nome_assunto(r: dict) -> str:
    i = str(r.get("id_assunto"))
    return ASSUNTOS.get(i, f"assunto {i}")


def idade_txt(r: dict) -> str:
    return f"{r['dias']} dias" if parse_dt(r.get("data_abertura")) else "sem data de abertura"


def resumo_tecnico(ixc: Ixc, tecnico_id: int, agora: datetime) -> dict:
    abertas = os_abertas(ixc, tecnico_id)
    completar_assuntos(ixc, [r.get("id_assunto") for r in abertas])
    grupos = classificar(abertas, agora)
    return {
        "tecnico_id": tecnico_id,
        "nome": TECNICOS.get(tecnico_id, f"técnico {tecnico_id}"),
        "abertas": len(abertas),
        "em_alerta": sum(len(grupos[k]) for k in ("criticas", "atencao", "recentes")),
        "pausadas": len(grupos["pausadas"]),
        "grupos": grupos,
    }


# --- Visão de gerente --------------------------------------------------------------------------


def texto_gerente(resumos: list[dict]) -> str:
    blocos = []
    t_ab = t_al = t_pa = 0
    for r in resumos:
        if not r["abertas"]:
            continue
        t_ab, t_al, t_pa = t_ab + r["abertas"], t_al + r["em_alerta"], t_pa + r["pausadas"]
        linhas = [f"👷 {r['nome']} — {r['abertas']} abertas | {r['em_alerta']} em alerta | {r['pausadas']} pausadas"]
        for chave, titulo in GRUPOS:
            lista = r["grupos"][chave]
            if lista:
                linhas.append(f"{titulo} ({len(lista)})")
                linhas += [f"• #{x['id']} · {nome_assunto(x)} · {idade_txt(x)}" for x in lista]
        blocos.append("\n".join(linhas))
    if not blocos:
        return ""
    blocos.append(f"📊 Total: {t_ab} abertas, {t_al} em alerta, {t_pa} pausadas")
    return "\n\n".join(blocos)


# --- Aviso pessoal do técnico --------------------------------------------------------------------


def destaques(r: dict) -> dict:
    """Fatos para o agente escrever a dica; nada aqui é opinião."""
    ativas = [x for g in ("criticas", "atencao", "recentes") for x in r["grupos"][g]]
    ativas.sort(key=lambda x: parse_dt(x.get("data_abertura")) or datetime.max)
    nao_assumidas = [x for x in ativas if not x["assumida"]]
    por_assunto: dict[str, int] = {}
    for x in ativas:
        por_assunto[nome_assunto(x)] = por_assunto.get(nome_assunto(x), 0) + 1
    assunto_top = max(por_assunto.items(), key=lambda kv: kv[1]) if por_assunto else None
    return {
        "mais_antiga": ativas[0] if ativas else None,
        "criticas": len(r["grupos"]["criticas"]),
        "nao_assumidas": len(nao_assumidas),
        "nao_assumida_mais_antiga": nao_assumidas[0] if nao_assumidas else None,
        "assunto_mais_comum": {"assunto": assunto_top[0], "quantidade": assunto_top[1]} if assunto_top else None,
    }


def texto_pessoal(r: dict, max_linhas: int = 10) -> str:
    if not r["abertas"]:
        return ""
    d = destaques(r)
    linhas = [f"☀️ Bom dia, {r['nome']}! Você tem {r['abertas']} O.S. abertas ({r['em_alerta']} em alerta, {r['pausadas']} pausadas)."]
    pontos = []
    if d["mais_antiga"]:
        x = d["mais_antiga"]
        pontos.append(f"• A mais antiga: #{x['id']} · {nome_assunto(x)} · {x['dias']} dias")
    if d["criticas"]:
        pontos.append(f"• {d['criticas']} com mais de 30 dias")
    if d["nao_assumidas"]:
        x = d["nao_assumida_mais_antiga"]
        pontos.append(f"• {d['nao_assumidas']} ainda sem data de assumida (a mais antiga: #{x['id']})")
    if d["assunto_mais_comum"] and d["assunto_mais_comum"]["quantidade"] >= 3:
        a = d["assunto_mais_comum"]
        pontos.append(f"• {a['quantidade']} são de {a['assunto']}")
    if pontos:
        linhas += ["", "🎯 Para dar atenção primeiro:"] + pontos
    ativas = [x for g in ("criticas", "atencao", "recentes") for x in r["grupos"][g]]
    ativas.sort(key=lambda x: parse_dt(x.get("data_abertura")) or datetime.max)
    if ativas:
        linhas += ["", f"📋 Mais antigas ({min(len(ativas), max_linhas)} de {len(ativas)} em alerta):"]
        linhas += [f"• #{x['id']} · {nome_assunto(x)} · {idade_txt(x)}" for x in ativas[:max_linhas]]
        if len(ativas) > max_linhas:
            linhas.append(f"…e mais {len(ativas) - max_linhas} O.S. em alerta")
    abertas_recentes = r["abertas"] - r["em_alerta"] - r["pausadas"]
    if abertas_recentes:
        linhas.append(f"🟢 Abertas há menos de 48 h: {abertas_recentes}")
    if r["pausadas"]:
        ids = ", ".join(f"#{x['id']}" for x in r["grupos"]["pausadas"][:10])
        linhas.append(f"⏸ Pausadas ({r['pausadas']}): {ids}")
    return "\n".join(linhas)


def dividir(texto: str) -> list[str]:
    """Partes de até 3800 caracteres, cortando só entre linhas inteiras."""
    partes, atual = [], ""
    for linha in texto.splitlines():
        candidato = atual + "\n" + linha if atual else linha
        if len(candidato) > LIMITE_TELEGRAM and atual:
            partes.append(atual)
            atual = linha
        else:
            atual = candidato
    if atual:
        partes.append(atual)
    return partes


def principal(argv=None, agora: datetime | None = None, ixc: Ixc | None = None) -> int:
    ap = argparse.ArgumentParser(description="Alerta de prazo das O.S. (somente leitura)")
    ap.add_argument("--modo", choices=("gerente", "pessoal"), required=True)
    ap.add_argument("--tecnicos", default="140,121,161", help="modo gerente: ids separados por vírgula")
    ap.add_argument("--tecnico", type=int, help="modo pessoal: id do técnico")
    ap.add_argument("--max-linhas", type=int, default=10)
    ap.add_argument("--so-dias-uteis", action="store_true", help="não imprime nada no sábado e no domingo")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    agora = agora or datetime.now(FUSO).replace(tzinfo=None)
    if a.so_dias_uteis and agora.weekday() >= 5:
        return 0
    if ixc is None:
        token = os.environ.get("IXC_TOKEN", "").strip()
        if ":" not in token:
            print("Erro: variável IXC_TOKEN ausente ou fora do formato id:hash.", file=sys.stderr)
            return 1
        ixc = Ixc(token, os.environ.get("IXC_BASE_URL", BASE_URL_PADRAO))
    try:
        if a.modo == "pessoal":
            if not a.tecnico:
                print("Erro: informe --tecnico no modo pessoal.", file=sys.stderr)
                return 1
            resumos = [resumo_tecnico(ixc, a.tecnico, agora)]
        else:
            ids = list(dict.fromkeys(int(x) for x in a.tecnicos.split(",") if x.strip()))
            resumos = [resumo_tecnico(ixc, t, agora) for t in ids]
    except (ErroIxc, ValueError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1

    if a.json:
        saida = []
        for r in resumos:
            item = {k: r[k] for k in ("tecnico_id", "nome", "abertas", "em_alerta", "pausadas")}
            item["grupos"] = {g: [{"id": x["id"], "assunto": nome_assunto(x), "dias": x["dias"], "assumida": x["assumida"]} for x in lista] for g, lista in r["grupos"].items()}
            if a.modo == "pessoal":
                d = destaques(r)
                item["destaques"] = {
                    "mais_antiga": {"id": d["mais_antiga"]["id"], "assunto": nome_assunto(d["mais_antiga"]), "dias": d["mais_antiga"]["dias"]} if d["mais_antiga"] else None,
                    "criticas": d["criticas"], "nao_assumidas": d["nao_assumidas"], "assunto_mais_comum": d["assunto_mais_comum"],
                }
            saida.append(item)
        if any(r["abertas"] for r in resumos):
            print(json.dumps(saida, ensure_ascii=False))
        return 0

    texto = texto_pessoal(resumos[0], a.max_linhas) if a.modo == "pessoal" else texto_gerente(resumos)
    if not texto:
        return 0
    print("\n\n<<<PARTE>>>\n\n".join(dividir(texto)) if len(texto) > LIMITE_TELEGRAM else texto)
    return 0


if __name__ == "__main__":
    sys.exit(principal())
