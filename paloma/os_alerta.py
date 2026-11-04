#!/usr/bin/env python3
"""Alerta de prazo das O.S. do IXC. Arquivo único, só biblioteca padrão do Python. SOMENTE LEITURA.

O PRÓPRIO SCRIPT consulta o IXC (como o migrar_avantia.py das migrações). O agente só chama o script e envia o texto.
O token NUNCA passa pelo agente: o script o lê sozinho e não o imprime em lugar nenhum. Ordem de busca do acesso:
  1) variáveis IXC_URL + IXC_TOKEN       2) arquivo indicado em IXC_TOKEN_FILE (chmod 600)
  3) dados/.ixc_acesso.json ao lado do script (chmod 600; criado pelo "acesso salvar" das migrações)
  4) cofre do agente: /opt/data/cofre-chaves.json (ou o caminho de IXC_COFRE): entrada "IXC" ou a primeira com tipo "ixc"
Se nenhuma existir, o script para com a mensagem "Erro: sem acesso ao IXC ...".

Uso:
  Testar o acesso (lê só 1 assunto; não imprime dados):
    os_alerta.py --testar-acesso
  Visão de gerente (Dona Socorro):
    os_alerta.py --modo gerente --tecnicos 140,121,161
  Aviso pessoal do técnico:
    os_alerta.py --modo pessoal --tecnico 140 --so-dias-uteis
  Dados em JSON (para responder perguntas pontuais): acrescente --json

Reserva (sem acesso do script): --entrada "ID=/opt/data/os_ID_p*.json" lê respostas cruas já salvas (uma página por
arquivo, {"page","total","registros":[...]}); aceita curinga e vários caminhos separados por vírgula.

O script confere que (1) as O.S. são do técnico pedido e (2) a quantidade bate com o "total" do IXC; se não bater, recusa
e diz o que falta. Do IXC ele usa só 5 campos (id, id_assunto, data_abertura, data_hora_assumido, status): nunca imprime
dado de cliente.

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
import base64
import glob
import json
import os
import re
import stat
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")
STATUS_FECHADAS = {"F"}
ASSUNTO_PAUSADO = "278"
ALERTA_H, ATENCAO_H, CRITICA_H = 48, 168, 720
LIMITE_TELEGRAM = 3800
BASE_URL_PADRAO = "https://gestorixc.webfoco.net/webservice/v1"
COFRE_PADRAO = "/opt/data/cofre-chaves.json"
MAX_PAGINAS = 60  # 1800 O.S. por técnico; se passar disso, o script recusa em vez de calcular com dados incompletos

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


_TOKEN_CONHECIDO: list[str] = []  # só para limpar o token de mensagens de erro; nunca é impresso


def _limpar(texto: str) -> str:
    for t in _TOKEN_CONHECIDO:
        texto = texto.replace(t, "[token]").replace(base64.b64encode(t.encode()).decode(), "[token]")
    return texto


def _ler_json_privado(caminho: str):
    try:
        modo = os.stat(caminho).st_mode
    except OSError:
        return None
    if modo & (stat.S_IRWXG | stat.S_IRWXO):
        raise ErroIxc(f"o arquivo {caminho} está com permissão aberta; rode chmod 600 nele")
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        raise ErroIxc(f"não consegui ler {caminho}") from None


def acesso_ixc(env=None) -> tuple[str, str, str]:
    """Devolve (url, token, origem). Nunca imprime o token."""
    env = os.environ if env is None else env
    if env.get("IXC_TOKEN"):
        return (env.get("IXC_URL") or BASE_URL_PADRAO), env["IXC_TOKEN"].strip(), "ambiente"
    if env.get("IXC_TOKEN_FILE"):
        dados = _ler_json_privado(env["IXC_TOKEN_FILE"])
        if isinstance(dados, dict) and dados.get("token"):
            return (env.get("IXC_URL") or dados.get("url") or BASE_URL_PADRAO), str(dados["token"]).strip(), "arquivo (IXC_TOKEN_FILE)"
    aqui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", ".ixc_acesso.json")
    dados = _ler_json_privado(aqui)
    if isinstance(dados, dict) and dados.get("token"):
        return (env.get("IXC_URL") or dados.get("url") or BASE_URL_PADRAO), str(dados["token"]).strip(), "acesso salvo"
    cofre = env.get("IXC_COFRE") or COFRE_PADRAO
    try:
        with open(cofre, encoding="utf-8") as f:
            itens = json.load(f)
    except (OSError, ValueError):
        itens = None
    if isinstance(itens, dict):
        entrada = next((v for k, v in itens.items() if str(k).lower() == "ixc" and isinstance(v, dict)), None)
        if entrada is None:
            entrada = next((v for v in itens.values() if isinstance(v, dict) and str(v.get("tipo", "")).lower() == "ixc"), None)
        if entrada and entrada.get("valor"):
            return (env.get("IXC_URL") or entrada.get("base_url") or BASE_URL_PADRAO), str(entrada["valor"]).strip(), "cofre do agente"
    raise ErroIxc("sem acesso ao IXC: não achei IXC_TOKEN, IXC_TOKEN_FILE, dados/.ixc_acesso.json nem a entrada do IXC no cofre do agente")


class Ixc:
    """Cliente só de leitura (POST com ixcsoft: listar). Não existe método de escrita nem de exclusão."""

    def __init__(self, url: str, token: str, timeout: float = 30.0):
        _TOKEN_CONHECIDO.append(token)
        self.url = url.rstrip("/")
        auth = base64.b64encode(token.encode()).decode()
        self.cab = {"Authorization": f"Basic {auth}", "Content-Type": "application/json", "ixcsoft": "listar"}
        self.timeout = timeout

    def listar(self, tabela: str, campo: str, valor: str, page: int = 1, rp: int = 30, id_desc: bool = False) -> tuple[list[dict], int | None]:
        corpo = {"qtype": f"{tabela}.{campo}", "query": str(valor), "oper": "=", "page": str(page), "rp": str(rp)}
        if id_desc:
            corpo.update({"sortname": f"{tabela}.id", "sortorder": "desc"})
        req = urllib.request.Request(f"{self.url}/{tabela}", data=json.dumps(corpo).encode(), headers=self.cab, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                dados = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise ErroIxc(f"IXC respondeu {e.code}") from None
        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
            raise ErroIxc("falha de rede ou resposta inválida do IXC") from None
        if isinstance(dados, dict) and dados.get("type") == "error":
            raise ErroIxc(_limpar(str(dados.get("message", "erro do IXC")))[:200])
        if not isinstance(dados, dict):
            raise ErroIxc("resposta inesperada do IXC")
        try:
            total = int(dados["total"])
        except (KeyError, TypeError, ValueError):
            total = None
        return [r for r in (dados.get("registros") or []) if isinstance(r, dict)], total


def registros_do_ixc(ixc: Ixc, tecnico_id: int) -> list[dict]:
    """Todas as páginas do técnico (mais recentes primeiro), com as mesmas conferências do modo arquivo."""
    regs: list[dict] = []
    totais: list[int] = []
    for pagina in range(1, MAX_PAGINAS + 1):
        lote, total = ixc.listar("su_oss_chamado", "id_tecnico", str(tecnico_id), page=pagina, id_desc=True)
        regs += lote
        if total is not None:
            totais.append(total)
        if len(lote) < 30 or (totais and len(regs) >= max(totais)):
            break
    return validar_registros(regs, totais, tecnico_id, f"IXC (técnico {tecnico_id})")


def completar_assuntos(ixc: Ixc, abertas: list[dict]) -> None:
    """Busca no IXC o nome dos assuntos ainda desconhecidos. Se falhar, o texto mostra 'assunto N'."""
    for i in {str(r.get("id_assunto")) for r in abertas if r.get("id_assunto") not in (None, "")} - set(ASSUNTOS):
        try:
            regs, _ = ixc.listar("su_oss_assunto", "id", i, rp=1)
        except ErroIxc:
            continue
        nome = str(regs[0].get("assunto", "")).strip() if regs else ""
        if nome:
            ASSUNTOS[i] = nome


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
    return validar_registros(regs, totais, tecnico_id, f"os arquivos de {padrao!r}")


def validar_registros(regs: list[dict], totais: list[int], tecnico_id: int, origem: str) -> list[dict]:
    unicos = {}
    for r in regs:
        unicos.setdefault(str(r.get("id")), r)  # a mesma página lida duas vezes não conta em dobro
    regs = list(unicos.values())
    errados = {str(r.get("id_tecnico")) for r in regs if r.get("id_tecnico") not in (None, "") and str(r.get("id_tecnico")) != str(tecnico_id)}
    if errados:
        raise ErroIxc(f"{origem} têm O.S. de outro técnico; refaça só o técnico {tecnico_id}")
    if totais and len(regs) != max(totais):
        raise ErroIxc(f"entrada incompleta para o técnico {tecnico_id}: {len(regs)} O.S. lidas e o IXC informou {max(totais)}; rode de novo")
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
    ap = argparse.ArgumentParser(description="Alerta de prazo das O.S. (consulta o IXC sozinho, somente leitura)")
    ap.add_argument("--modo", choices=("gerente", "pessoal"))
    ap.add_argument("--testar-acesso", action="store_true", help="só confere o acesso ao IXC e diz de onde veio; não imprime dados")
    ap.add_argument("--tecnicos", default="140,121,161", help="modo gerente: ids separados por vírgula")
    ap.add_argument("--tecnico", type=int, help="modo pessoal: id do técnico")
    ap.add_argument("--max-linhas", type=int, default=10)
    ap.add_argument("--so-dias-uteis", action="store_true", help="não imprime nada no sábado e no domingo")
    ap.add_argument("--entrada", action="append", default=[], metavar="ID=CAMINHO",
                    help='RESERVA: arquivos já salvos; "ID=/opt/data/os_ID_p*.json" (repita por técnico). Sem isso o script consulta o IXC')
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.testar_acesso:
        try:
            url, token, origem = acesso_ixc()
            Ixc(url, token).listar("su_oss_assunto", "id", ASSUNTO_PAUSADO, rp=1)
        except ErroIxc as e:
            print(f"Erro: {_limpar(str(e))}", file=sys.stderr)
            return 1
        print(f"acesso vindo de: {origem}\nacesso OK (leitura)")
        return 0
    if not a.modo:
        print("Erro: informe --modo gerente|pessoal (ou --testar-acesso).", file=sys.stderr)
        return 1
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
        ixc = None
        if any(t not in entradas for t in ids):
            url, token, _ = acesso_ixc()
            ixc = Ixc(url, token)
        listas = {t: abertas_de_registros(registros_dos_arquivos(entradas[t], t) if t in entradas else registros_do_ixc(ixc, t)) for t in ids}
        if ixc:
            completar_assuntos(ixc, [r for l in listas.values() for r in l])
        resumos = [resumo_tecnico(t, agora, listas[t]) for t in ids]
    except (ErroIxc, ValueError) as e:
        print(f"Erro: {_limpar(str(e))}", file=sys.stderr)
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
