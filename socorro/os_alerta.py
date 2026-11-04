#!/usr/bin/env python3
"""Alerta de prazo das O.S. do IXC. Arquivo único, só biblioteca padrão do Python. SEM TOKEN, SEM REDE, SOMENTE LEITURA.

Quem fala com o IXC é o agente, pela ferramenta api_integracao (como nas migrações). O agente salva as respostas
em arquivos e este script só LÊ os arquivos, classifica e formata a mensagem.

Uso:
  Visão de gerente (Dona Socorro):
    os_alerta.py --modo gerente --tecnicos 140,121,161 --entrada "140=/opt/data/os_140_p*.json" --entrada "121=/opt/data/os_121_p*.json" --entrada "161=/opt/data/os_161_p*.json"
  Aviso pessoal do técnico:
    os_alerta.py --modo pessoal --tecnico 140 --so-dias-uteis --entrada "/opt/data/os_140_p*.json"
  Dados em JSON (para responder perguntas pontuais): acrescente --json

Arquivos de entrada: a RESPOSTA CRUA da listagem, uma página por arquivo ({"page","total","registros":[...]}), com todas as
páginas do técnico (tabela su_oss_chamado, filtro id_tecnico). --entrada aceita curinga (*) e vários caminhos separados
por vírgula. O script confere que (1) as O.S. são do técnico pedido e (2) a quantidade bate com o "total" do IXC; se não
bater, recusa e diz o que falta. Do arquivo ele usa só 5 campos (id, id_assunto, data_abertura, data_hora_assumido,
status): nunca imprime dado de cliente.

Regras (confirmadas com o Henrique em 03/11/2026):
  aberta  = status diferente de "F"
  pausada = id_assunto 278 (Pausado/Congelado)
  alerta  = aberta há mais de 48 h desde data_abertura, exceto pausadas (horário de Brasília)
  grupos  = 🔴 mais de 30 dias | 🟠 7 a 30 dias | 🟡 48 h a 7 dias

Se não houver nada a avisar, não imprime NADA e sai com código 0: o agente não deve enviar mensagem.
Erros vão para o stderr ("Erro: ...") com código 1.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")
STATUS_FECHADAS = {"F"}
ASSUNTO_PAUSADO = "278"
ALERTA_H, ATENCAO_H, CRITICA_H = 48, 168, 720
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


def parse_dt(valor):
    if not valor or str(valor).startswith("0000"):
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(valor), fmt)
        except ValueError:
            pass
    return None


CAMPOS = ("id", "id_assunto", "data_abertura", "data_hora_assumido", "status")


def arquivos_de(padrao: str) -> list[str]:
    """Expande curingas e vírgulas, em ordem estável. Erro claro se nada for encontrado."""
    achados: list[str] = []
    for p in (x.strip() for x in padrao.split(",") if x.strip()):
        achados += sorted(glob.glob(p)) or []
    achados = list(dict.fromkeys(achados))
    if not achados:
        raise ErroIxc(f"nenhum arquivo encontrado em {padrao!r}; salve a resposta de cada página da listagem em /opt/data")
    return achados


def registros_dos_arquivos(padrao: str, tecnico_id: int) -> list[dict]:
    """Junta as páginas salvas pelo agente (resposta crua do IXC), sem repetir O.S. e conferindo integridade."""
    regs: list[dict] = []
    totais: list[int] = []
    for caminho in arquivos_de(padrao):
        try:
            with open(caminho, encoding="utf-8") as f:
                dados = json.load(f)
        except (OSError, ValueError):
            raise ErroIxc(f"não consegui ler {caminho} (ausente ou não é JSON)") from None
        itens = dados if isinstance(dados, list) else [dados]
        for item in itens:
            if not isinstance(item, dict):
                raise ErroIxc(f"formato inesperado em {caminho}")
            if "registros" in item:
                regs += [r for r in (item.get("registros") or []) if isinstance(r, dict)]
                try:
                    totais.append(int(item["total"]))
                except (KeyError, TypeError, ValueError):
                    pass
            else:
                regs.append(item)
    unicos = {}
    for r in regs:
        unicos.setdefault(str(r.get("id")), r)  # a mesma página salva duas vezes não conta em dobro
    regs = list(unicos.values())
    errados = {str(r.get("id_tecnico")) for r in regs if r.get("id_tecnico") not in (None, "") and str(r.get("id_tecnico")) != str(tecnico_id)}
    if errados:
        raise ErroIxc(f"os arquivos de {padrao!r} têm O.S. de outro técnico; busque de novo só o técnico {tecnico_id}")
    if totais and len(regs) != max(totais):
        raise ErroIxc(f"entrada incompleta para o técnico {tecnico_id}: {len(regs)} O.S. nos arquivos e o IXC informou {max(totais)}; busque as páginas que faltam e salve de novo")
    return regs


def abertas_de_registros(regs: list[dict]) -> list[dict]:
    return [{c: r.get(c) for c in CAMPOS} for r in regs if r.get("status") not in STATUS_FECHADAS]


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


def resumo_tecnico(tecnico_id: int, agora: datetime, abertas: list[dict]) -> dict:
    grupos = classificar(abertas, agora)
    return {
        "tecnico_id": tecnico_id,
        "nome": TECNICOS.get(tecnico_id, f"técnico {tecnico_id}"),
        "abertas": len(abertas),
        "em_alerta": sum(len(grupos[k]) for k in ("criticas", "atencao", "recentes")),
        "pausadas": len(grupos["pausadas"]),
        "grupos": grupos,
    }


# --- Visão de gerente ----------------------------------------------------------------------------


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


def principal(argv=None, agora: datetime | None = None) -> int:
    ap = argparse.ArgumentParser(description="Alerta de prazo das O.S. (lê arquivos salvos pelo agente; sem token e sem rede)")
    ap.add_argument("--modo", choices=("gerente", "pessoal"), required=True)
    ap.add_argument("--tecnicos", default="140,121,161", help="modo gerente: ids separados por vírgula")
    ap.add_argument("--tecnico", type=int, help="modo pessoal: id do técnico")
    ap.add_argument("--max-linhas", type=int, default=10)
    ap.add_argument("--so-dias-uteis", action="store_true", help="não imprime nada no sábado e no domingo")
    ap.add_argument("--entrada", action="append", default=[], metavar="ID=CAMINHO",
                    help='arquivos da listagem; "ID=/opt/data/os_ID_p*.json" (repita por técnico; no modo pessoal pode ser só o caminho)')
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    agora = agora or datetime.now(FUSO).replace(tzinfo=None)
    if a.so_dias_uteis and agora.weekday() >= 5:
        return 0
    entradas: dict[int, str] = {}
    for e in a.entrada:
        if "=" in e:
            k, _, v = e.partition("=")
            try:
                entradas[int(k)] = v
            except ValueError:
                print(f"Erro: --entrada inválido ({k!r} não é id de técnico).", file=sys.stderr)
                return 1
        elif a.modo == "pessoal" and a.tecnico:
            entradas[a.tecnico] = e
        else:
            print("Erro: use --entrada ID=CAMINHO.", file=sys.stderr)
            return 1
    try:
        if a.modo == "pessoal":
            if not a.tecnico:
                print("Erro: informe --tecnico no modo pessoal.", file=sys.stderr)
                return 1
            ids = [a.tecnico]
        else:
            ids = list(dict.fromkeys(int(x) for x in a.tecnicos.split(",") if x.strip()))
        faltando = [t for t in ids if t not in entradas]
        if faltando:
            print(f"Erro: falta --entrada para o técnico {faltando[0]}.", file=sys.stderr)
            return 1
        resumos = [resumo_tecnico(t, agora, abertas_de_registros(registros_dos_arquivos(entradas[t], t))) for t in ids]
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
