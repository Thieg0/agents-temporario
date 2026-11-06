#!/usr/bin/env python3
"""os_detalhe.py: detalhes e atualizações de uma O.S. do IXC (SOMENTE LEITURA).

Uso (o agente descobre os parâmetros pela mensagem da pessoa; este script nunca recebe a frase dela):
  python3 os_detalhe.py --os 76580                 detalhes + últimas atualizações da O.S.
  python3 os_detalhe.py --os 76580 --ultimas 10    mostra as 10 atualizações mais recentes (padrão 5)
  python3 os_detalhe.py --buscar "SDR BRM 83104884"           procura O.S. pela designação/texto da descrição
  python3 os_detalhe.py --buscar 7386 --por contrato          procura pelo id do contrato (ou --por cliente)
  python3 os_detalhe.py --testar-acesso

O que mostra: status, assunto, responsável, datas, descrição (campo mensagem) e a resposta/fechamento (mensagem_resposta).
Se o token tiver permissão na tabela de mensagens da O.S. (su_oss_chamado_mensagem), mostra também o histórico de
atualizações; se não tiver, avisa na saída e segue só com os campos da O.S. Nunca imprime endereço, telefone nem token.
Erros vão para o stderr ("Erro: ...") com código 1. Não existe nenhum método de escrita neste script.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import stat
import sys
import urllib.error
import urllib.request
from datetime import datetime

BASE_URL_PADRAO = "https://gestorixc.webfoco.net/webservice/v1"
COFRE_PADRAO = "/opt/data/cofre-chaves.json"
LIMITE_TELEGRAM = 3800
STATUS = {"A": "Aberta", "AN": "Em análise", "EN": "Encaminhada", "AS": "Assumida", "AG": "Agendada", "EX": "Em execução", "F": "Finalizada", "C": "Cancelada"}
PRIORIDADE = {"B": "Baixa", "N": "Normal", "A": "Alta", "C": "Crítica"}
ASSUNTOS = {"5": "Ativação de cliente", "20": "Vistoria Interna", "55": "Geral", "56": "Ativação", "74": "Alteração de Endereço",
            "212": "Criação de PPI", "235": "Mudança de Titularidade", "256": "Registro de Tratativa", "278": "Pausado/Congelado"}
TECNICOS = {140: "Milena", 121: "Luiz Felipe", 161: "Edson", 118: "Carlos Henrique", 144: "Raissa (comercial)", 139: "Paloma", 24: "Socorro", 176: "Bruna",
            179: "Celso", 145: "Daiana", 120: "Eliseu", 184: "Jennypher", 148: "Maria Eduarda", 71: "Fernando", 101: "Marina", 25: "Rafael",
            114: "Raissa (NOC)", 178: "João Vítor", 14: "Julio"}
MAX_TEXTO = 700
TABELA_MENSAGENS = "su_oss_chamado_mensagem"


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

    def listar(self, tabela: str, campo: str, valor: str, page: int = 1, rp: int = 30, id_desc: bool = False, oper: str = "=") -> tuple[list[dict], int | None]:
        corpo = {"qtype": f"{tabela}.{campo}", "query": str(valor), "oper": oper, "page": str(page), "rp": str(rp)}
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




def nome_status(codigo: str) -> str:
    return STATUS.get(str(codigo or "").strip(), str(codigo or "não informado"))


def nome_assunto(ixc: "Ixc | None", codigo: str) -> str:
    codigo = str(codigo or "").strip()
    if codigo in ASSUNTOS:
        return ASSUNTOS[codigo]
    if ixc is not None and codigo:
        try:
            regs, _ = ixc.listar("su_oss_assunto", "id", codigo, rp=1)
            if regs and regs[0].get("assunto"):
                return str(regs[0]["assunto"])
        except ErroIxc:
            pass
    return f"assunto {codigo}" if codigo else "não informado"


def nome_tecnico(codigo: str) -> str:
    try:
        n = int(str(codigo).strip())
    except ValueError:
        return "não informado"
    return TECNICOS.get(n) or f"funcionário {n}"


def fmt_dt(valor) -> str:
    d = parse_dt(valor)
    return d.strftime("%d/%m/%Y %H:%M") if d else "-"


def cortar(texto: str, limite: int = MAX_TEXTO) -> str:
    texto = (texto or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    return texto if len(texto) <= limite else texto[:limite].rstrip() + " (…texto cortado)"


def historico(ixc: Ixc, os_id: str, n: int) -> tuple[list[dict], str | None]:
    """Últimas n atualizações da tabela de mensagens. Devolve (lista, aviso). Sem permissão => ([], aviso)."""
    try:
        regs, _ = ixc.listar(TABELA_MENSAGENS, "id_chamado", os_id, rp=n, id_desc=True)
    except ErroIxc as e:
        return [], f"histórico completo indisponível para este acesso ({e}); mostrando só os campos da O.S."
    return regs, None


def texto_os(r: dict, ixc: Ixc, ultimas: int) -> str:
    os_id = str(r.get("id", ""))
    linhas = [f"O.S. {os_id}",
              f"Status: {nome_status(r.get('status'))}",
              f"Assunto: {nome_assunto(ixc, r.get('id_assunto'))}",
              f"Responsável: {nome_tecnico(r.get('id_tecnico'))}"]
    prio = PRIORIDADE.get(str(r.get("prioridade", "")).strip())
    if prio:
        linhas.append(f"Prioridade: {prio}")
    if r.get("id_cliente"):
        linhas.append(f"Cliente (id): {r['id_cliente']}" + (f" | contrato (id): {r['id_contrato_kit']}" if r.get("id_contrato_kit") not in (None, "", "0") else ""))
    linhas += [f"Aberta em: {fmt_dt(r.get('data_abertura'))}",
               f"Assumida em: {fmt_dt(r.get('data_hora_assumido'))}",
               f"Executada em: {fmt_dt(r.get('data_hora_execucao'))}",
               f"Finalizada em: {fmt_dt(r.get('data_fechamento'))}",
               "", "Descrição (campo mensagem):", cortar(r.get("mensagem", "")) or "(vazia)"]
    resp = cortar(r.get("mensagem_resposta", ""))
    if resp:
        linhas += ["", "Resposta / fechamento (campo mensagem_resposta):", resp]
    regs, aviso = historico(ixc, os_id, ultimas)
    if regs:
        linhas += ["", f"Últimas {len(regs)} atualizações (mais recente primeiro):"]
        for h in regs:
            quando = fmt_dt(h.get("data") or h.get("data_hora") or h.get("data_cadastro"))
            quem = h.get("id_usuarios") or h.get("id_funcionario") or h.get("id_tecnico") or ""
            quem_txt = f" - {nome_tecnico(quem)}" if str(quem).strip() not in ("", "0") else ""
            linhas.append(f"- {quando}{quem_txt}: {cortar(str(h.get('mensagem', '')), 400) or '(sem texto)'}")
    elif aviso:
        linhas += ["", "Aviso: " + aviso]
    return "\n".join(linhas)


def linha_busca(r: dict) -> str:
    primeira = cortar(r.get("mensagem", ""), 90).split("\n")[0]
    return f"- O.S. {r.get('id')} | {nome_status(r.get('status'))} | aberta {fmt_dt(r.get('data_abertura'))} | {primeira}"


POR = {"designacao": ("mensagem", "L"), "texto": ("mensagem", "L"), "cliente": ("id_cliente", "="), "contrato": ("id_contrato_kit", "=")}


def principal(argv=None, env=None) -> int:
    ap = argparse.ArgumentParser(description="Detalhes e atualizações de uma O.S. do IXC (somente leitura)")
    ap.add_argument("--os", help="número da O.S.")
    ap.add_argument("--buscar", help="texto/designação ou id para procurar O.S.")
    ap.add_argument("--por", choices=sorted(POR), default="designacao", help="onde procurar com --buscar (padrão: designacao)")
    ap.add_argument("--ultimas", type=int, default=5, help="quantas atualizações mostrar (padrão 5, máximo 30)")
    ap.add_argument("--limite", type=int, default=10, help="máximo de O.S. na busca (padrão 10)")
    ap.add_argument("--testar-acesso", action="store_true")
    a = ap.parse_args(argv)
    a.ultimas = max(1, min(a.ultimas, 30))
    try:
        url, token, origem = acesso_ixc(env)
        ixc = Ixc(url, token)
        if a.testar_acesso:
            ixc.listar("su_oss_chamado", "id", "1", rp=1)
            print(f"acesso OK (origem do acesso: {origem})")
            return 0
        if a.os:
            if not str(a.os).strip().isdigit():
                raise ErroIxc("o número da O.S. deve conter só dígitos")
            regs, _ = ixc.listar("su_oss_chamado", "id", str(a.os).strip(), rp=1)
            if not regs:
                raise ErroIxc(f"O.S. {a.os} não encontrada")
            print(texto_os(regs[0], ixc, a.ultimas))
            return 0
        if a.buscar:
            campo, oper = POR[a.por]
            termo = a.buscar.strip()
            if not termo:
                raise ErroIxc("informe o que procurar")
            regs, total = ixc.listar("su_oss_chamado", campo, termo, rp=max(1, min(a.limite, 30)), id_desc=True, oper=oper)
            if not regs:
                print("Nenhuma O.S. encontrada para esta busca.")
                return 0
            if len(regs) == 1:
                print(texto_os(regs[0], ixc, a.ultimas))
                return 0
            print(f"Encontrei {total if total is not None else len(regs)} O.S. (mostrando as {len(regs)} mais recentes). Diga qual número você quer ver:")
            for r in regs:
                print(linha_busca(r))
            return 0
        ap.error("informe --os, --buscar ou --testar-acesso")
    except ErroIxc as e:
        print(f"Erro: {_limpar(str(e))}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(principal())
