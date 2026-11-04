#!/usr/bin/env python3
"""NOC: prepara a abertura de OS no IXC a partir da designação. SOMENTE LEITURA: não grava nada no IXC.

O PRÓPRIO SCRIPT consulta o IXC (token do cofre do agente, de IXC_TOKEN, IXC_TOKEN_FILE ou dados/.ixc_acesso.json; o
agente nunca vê o token). Fluxo do NOC (Jennypher, 03/11/2026):
  1) acha as OS com a mesma designação e usa a mais recente FINALIZADA como modelo (avisa se já existe OS aberta);
  2) dela tira o cliente e o contrato; do nome do contrato tira o "cliente final";
  3) monta a descrição no modelo oficial, que o humano confere e usa para abrir a OS (assunto 55, Geral).

Uso:
  preparar_os.py --designacao "SDR TAF 83108054" --chamado "OEMP-42074" --motivo "Inoperante"
  preparar_os.py --designacao "SDR TAF 83108054" --descobrir     (só nomes de campos; para calibrar)
Opções: --json (saída em JSON)

Para e manda para o humano (nunca chuta) quando: nenhuma OS com a designação; OS com contratos diferentes; contrato sem nome
no formato esperado. Erros vão para o stderr ("Erro: ...") com código 1. Não imprime telefone, e-mail nem endereço de cliente.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import stat
import sys
import urllib.error
import urllib.request

BASE_URL_PADRAO = "https://gestorixc.webfoco.net/webservice/v1"
COFRE_PADRAO = "/opt/data/cofre-chaves.json"
ASSUNTO_GERAL = "55"
LINHAS_DESCRICAO = ("Designação / Vlan", "Cliente Final", "Chamado interno", "Motivo do chamado")


class ErroIxc(RuntimeError):
    pass


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



def norm(txt) -> str:
    return re.sub(r"\s+", "", str(txt or "")).casefold()


def cliente_final(nome_contrato: str) -> str | None:
    """'8054 - Video Policia -SEAP-I-078 - Teixeira de Freitas - ...' -> 'Video Policia -SEAP-I-078'."""
    m = re.match(r"^\s*\d+\s*-\s*(.+?)\s+-\s+\S", str(nome_contrato or ""))
    if m:
        return m.group(1).strip()
    m = re.match(r"^\s*\d+\s*-\s*(.+?)\s*$", str(nome_contrato or ""))
    return m.group(1).strip() if m and " - " not in m.group(1) else None


def achar_os(ixc: Ixc, designacao: str) -> list[dict]:
    regs, _ = ixc.listar("su_oss_chamado", "mensagem", designacao, rp=20, id_desc=True, oper="L")
    alvo = norm(designacao)
    return [r for r in regs if alvo in norm(r.get("mensagem"))]


def preparar(ixc: Ixc, designacao: str, chamado: str, motivo: str) -> dict:
    designacao = designacao.strip()
    if not designacao:
        raise ErroIxc("informe a designação")
    achadas = achar_os(ixc, designacao)
    if not achadas:
        raise ErroIxc(f"PARAR: nenhuma OS no IXC com a designação {designacao!r}. Confira o texto e, se estiver certo, o humano abre a OS pelo caminho manual.")
    contratos = {str(r.get("id_contrato")) for r in achadas if r.get("id_contrato") not in (None, "", "0")}
    if len(contratos) != 1:
        lista = ", ".join(f"OS {r.get('id')} (contrato {r.get('id_contrato')})" for r in achadas[:8])
        raise ErroIxc(f"PARAR: as OS com essa designação não apontam para um único contrato ({lista}). O humano decide.")
    abertas = [r for r in achadas if r.get("status") != "F"]
    finalizadas = [r for r in achadas if r.get("status") == "F"]
    modelo = finalizadas[0] if finalizadas else achadas[0]  # a mais recente finalizada (o IXC devolve da mais nova para a mais antiga)
    contrato_id = contratos.pop()
    cts, _ = ixc.listar("cliente_contrato", "id", contrato_id, rp=1)
    if not cts:
        raise ErroIxc(f"PARAR: não achei o contrato {contrato_id} no IXC.")
    ct = cts[0]
    nome = str(ct.get("contrato") or "").strip()
    final = cliente_final(nome)
    avisos = []
    if abertas:
        avisos.append("JÁ EXISTE OS ABERTA com essa designação (" + ", ".join(str(r.get("id")) for r in abertas[:5]) + "): confirme com o NOC antes de abrir outra (risco de OS duplicada)")
    if not finalizadas:
        avisos.append("nenhuma OS finalizada com essa designação; o contrato foi lido de uma OS aberta")
    if not final:
        avisos.append("não consegui tirar o Cliente Final do nome do contrato: preencha na mão")
    if str(ct.get("status", "A")) != "A":
        avisos.append(f"contrato com status {ct.get('status')!r} (esperado A, ativo): confira antes de abrir")
    if norm(designacao) not in norm(ct.get("descricao_aux_plano_venda")):
        avisos.append("a designação não aparece na descrição auxiliar do contrato: confira se é o contrato certo")
    cliente_id = str(modelo.get("id_cliente") or ct.get("id_cliente") or "")
    campos = {
        "Designação / Vlan": designacao,
        "Cliente Final": final or "[preencher]",
        "Chamado interno": chamado.strip() or "[preencher]",
        "Motivo do chamado": motivo.strip() or "[preencher]",
    }
    if not chamado.strip():
        avisos.append("faltou o chamado interno (OEMP, e-mail ou Opa)")
    if not motivo.strip():
        avisos.append("faltou o motivo do chamado")
    return {
        "os_modelo": str(modelo.get("id")),
        "os_com_a_designacao": len(achadas),
        "assunto": ASSUNTO_GERAL,
        "cliente": cliente_id,
        "contrato": contrato_id,
        "contrato_nome": f"{contrato_id} - {final}" if final else f"{contrato_id} (nome fora do formato)",
        "descricao": "\n".join(f"{k}: {v}" for k, v in campos.items()),
        "avisos": avisos,
    }


def texto(p: dict) -> str:
    linhas = [
        "📝 OS PREPARADA (nada foi gravado no IXC)",
        f"Assunto: {p['assunto']} (Geral)  |  Cliente: {p['cliente']}  |  Contrato: {p['contrato']}",
        f"Contrato no IXC: {p['contrato_nome']}",
        f"Prioridade: a confirmar com o NOC  |  Endereço e filial: copiar da OS {p['os_modelo']} (anterior, mesma designação)",
        "",
        "Descrição (copiar e colar, sem as linhas extras):",
        p["descricao"],
        "",
        f"Base: OS {p['os_modelo']} (a mais recente finalizada; {p['os_com_a_designacao']} OS com essa designação, todas no mesmo contrato).",
    ]
    if p["avisos"]:
        linhas += ["", "⚠️ Conferir antes de abrir:"] + [f"• {a}" for a in p["avisos"]]
    return "\n".join(linhas)


def descobrir(ixc: Ixc, designacao: str) -> str:
    achadas = achar_os(ixc, designacao)
    if not achadas:
        raise ErroIxc("nenhuma OS com essa designação")
    m = achadas[0]
    seguros = ("id", "id_assunto", "status", "id_contrato", "id_cliente", "id_filial", "id_setor", "setor", "prioridade", "origem_endereco", "id_tecnico", "data_abertura")
    linhas = [f"OS modelo {m.get('id')} ({len(achadas)} com a designação). Campos (só nomes; valores só dos técnicos):", "  " + ", ".join(sorted(m.keys())), "Valores técnicos:"]
    linhas += [f"  {k} = {m.get(k)!r}" for k in seguros if k in m]
    cts, _ = ixc.listar("cliente_contrato", "id", str(m.get("id_contrato")), rp=1)
    if cts:
        linhas += ["Contrato (só nomes de campos):", "  " + ", ".join(sorted(cts[0].keys()))]
    return "\n".join(linhas)


def principal(argv=None) -> int:
    ap = argparse.ArgumentParser(description="NOC: prepara a abertura de OS (somente leitura)")
    ap.add_argument("--designacao", required=True)
    ap.add_argument("--chamado", default="")
    ap.add_argument("--motivo", default="")
    ap.add_argument("--descobrir", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        url, token, _ = acesso_ixc()
        ixc = Ixc(url, token)
        if a.descobrir:
            print(descobrir(ixc, a.designacao))
            return 0
        p = preparar(ixc, a.designacao, a.chamado, a.motivo)
    except ErroIxc as e:
        print(f"Erro: {_limpar(str(e))}", file=sys.stderr)
        return 1
    print(json.dumps(p, ensure_ascii=False) if a.json else texto(p))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
