#!/usr/bin/env python3
"""NOC: prepara, ABRE e EXECUTA OS no IXC a partir da designação. Por padrão é SIMULAÇÃO (não grava); só grava com --gravar.

O PRÓPRIO SCRIPT consulta o IXC (token do cofre do agente, de IXC_TOKEN, IXC_TOKEN_FILE ou dados/.ixc_acesso.json; o
agente nunca vê o token). Fluxo do NOC (Jennypher, 03/11/2026):
  1) acha as OS com a mesma designação e usa a mais recente FINALIZADA como modelo (avisa se já existe OS aberta);
  2) dela tira o cliente e o contrato; do nome do contrato tira o "cliente final";
  3) monta a descrição no modelo oficial, que o humano confere e usa para abrir a OS (assunto 55, Geral).

Uso:
  preparar_os.py --designacao "SDR TAF 83108054" --chamado "OEMP-42074" --motivo "Inoperante"
  preparar_os.py --designacao "SDR TAF 83108054" --descobrir     (só nomes de campos; para calibrar)
  preparar_os.py --comparar 75811 76196                          (campos que diferem entre duas OS; para calibrar a gravação)
  preparar_os.py --funcionarios "nome"                           (id + nome do colaborador, para o --colaborador)
  preparar_os.py --abrir --designacao ... --chamado ... --motivo ... --colaborador 184 [--gravar]
        simula (mostra o que seria gravado); com --gravar abre a OS e imprime "ID DA OS: N" (ID vem só da resposta do IXC)
  preparar_os.py --executar-os 76388 [--mensagem "..."] [--colaborador 184] [--gravar]
        Ações > Executar na OS (padrão da mensagem: "Acionado parceiro via WhatsApp"); simula sem --gravar
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
from datetime import datetime, timedelta, timezone

BASE_URL_PADRAO = "https://gestorixc.webfoco.net/webservice/v1"
COFRE_PADRAO = "/opt/data/cofre-chaves.json"
ASSUNTO_GERAL = "55"
FILIAL_NOC = "2"
SETOR_NOC = "14"
MSG_EXECUTAR = "Acionado parceiro via WhatsApp"
CAMPOS_ENDERECO = ("endereco", "numero", "bairro", "complemento", "cep")  # copiados do cadastro do cliente; nunca impressos
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

    def enviar(self, tabela: str, corpo: dict) -> dict:
        """POST de gravação (sem o cabeçalho 'listar'). Devolve o JSON do IXC; levanta ErroIxc se o IXC recusar."""
        cab = {k: v for k, v in self.cab.items() if k != "ixcsoft"}
        req = urllib.request.Request(f"{self.url}/{tabela}", data=json.dumps(corpo).encode(), headers=cab, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                dados = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise ErroIxc(f"IXC respondeu {e.code} ao gravar") from None
        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
            raise ErroIxc("falha de rede ou resposta inválida do IXC ao gravar (confira no IXC se a gravação aconteceu antes de repetir)") from None
        if not isinstance(dados, dict):
            raise ErroIxc("resposta inesperada do IXC ao gravar")
        if dados.get("type") == "error":
            raise ErroIxc(_limpar(str(dados.get("message", "erro do IXC")))[:300])
        return dados


def norm(txt) -> str:
    return re.sub(r"\s+", "", str(txt or "")).casefold()


def cliente_final(nome_contrato: str) -> str | None:
    """'8054 - Video Policia -SEAP-I-078 - Teixeira de Freitas - ...' -> 'Video Policia -SEAP-I-078'."""
    m = re.match(r"^\s*\d+\s*-\s*(.+?)\s+-\s+\S", str(nome_contrato or ""))
    if m:
        return m.group(1).strip()
    m = re.match(r"^\s*\d+\s*-\s*(.+?)\s*$", str(nome_contrato or ""))
    return m.group(1).strip() if m and " - " not in m.group(1) else None


def contrato_da_os(r: dict) -> str:
    """Contrato da OS: id_contrato, ou id_contrato_kit (campo que o IXC preenche nas OS do NOC)."""
    for k in ("id_contrato", "id_contrato_kit"):
        v = str(r.get(k) or "").strip()
        if v not in ("", "0"):
            return v
    return ""


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
    contratos = {contrato_da_os(r) for r in achadas if contrato_da_os(r)}
    if len(contratos) != 1:
        lista = ", ".join(f"OS {r.get('id')} (contrato {contrato_da_os(r) or '?'})" for r in achadas[:8])
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
    cts, _ = ixc.listar("cliente_contrato", "id", contrato_da_os(m), rp=1)
    if cts:
        linhas += ["Contrato (só nomes de campos):", "  " + ", ".join(sorted(cts[0].keys()))]
    return "\n".join(linhas)


SENSIVEL = ("fone", "mail", "cpf", "cnpj", "senha", "token", "celular", "whats")


def ler_os(ixc: Ixc, os_id: str) -> dict:
    regs, _ = ixc.listar("su_oss_chamado", "id", str(os_id).strip(), rp=1)
    if not regs:
        raise ErroIxc(f"não achei a OS {os_id} no IXC")
    return regs[0]


def comparar(ixc: Ixc, a: str, b: str, iguais_valores: bool = False) -> str:
    """Só leitura: mostra os campos que diferem entre duas OS (valores curtos; campos de contato ficam de fora)."""
    ra, rb = ler_os(ixc, a), ler_os(ixc, b)
    chaves = sorted(set(ra) | set(rb))
    iguais, difer, so_a, so_b, ig_val = 0, [], [], [], []
    for k in chaves:
        if any(x in k.lower() for x in SENSIVEL):
            continue
        if k not in rb:
            so_a.append(k)
        elif k not in ra:
            so_b.append(k)
        elif str(ra[k]) == str(rb[k]):
            iguais += 1
            if str(ra[k]).strip() and len(str(ra[k])) <= 24:
                ig_val.append(f"{k}={ra[k]!r}")
        else:
            difer.append(k)
    cur = lambda v: (str(v)[:70] + "…") if len(str(v)) > 70 else str(v)  # noqa: E731
    linhas = [f"OS {a} x OS {b}: {iguais} campos iguais, {len(difer)} diferentes.", "Diferentes (campo: valor em A | valor em B):"]
    linhas += [f"  {k}: {cur(ra[k])!r} | {cur(rb[k])!r}" for k in difer]
    if iguais_valores:
        linhas += ["Iguais (campo=valor, só os curtos e preenchidos):", "  " + ", ".join(ig_val)]
    if so_a:
        linhas.append("Só na A: " + ", ".join(so_a))
    if so_b:
        linhas.append("Só na B: " + ", ".join(so_b))
    return "\n".join(linhas)


ZERO_DATA = "0000-00-00 00:00:00"


def agora_br() -> str:
    return datetime.now(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M:%S")


def achar_colaborador(ixc: Ixc, colaborador: str) -> tuple[str, str]:
    cid = str(colaborador or "").strip()
    if not cid.isdigit():
        raise ErroIxc("informe --colaborador com o NÚMERO (id) do colaborador; use --funcionarios \"nome\" para descobrir")
    regs, _ = ixc.listar("funcionarios", "id", cid, rp=1)
    regs = [r for r in regs if str(r.get("id")) == cid]
    if not regs:
        raise ErroIxc(f"PARAR: não achei o colaborador de id {cid} no IXC")
    return cid, str(regs[0].get("funcionario") or "").strip()


def _endereco_da_ultima_os(ixc: Ixc, cliente_id: str) -> tuple[dict, str]:
    """Plano B quando o token não lê o cadastro de clientes: usa o endereço da OS mais recente do mesmo cliente no NOC."""
    for pagina in (1, 2, 3):
        regs, _ = ixc.listar("su_oss_chamado", "id_cliente", cliente_id, page=pagina, rp=30, id_desc=True)
        for r in regs:
            if str(r.get("setor") or r.get("id_setor") or "") == SETOR_NOC and str(r.get("id_assunto")) == ASSUNTO_GERAL \
                    and any(str(r.get(k) or "").strip() for k in ("bairro", "endereco", "cep")):
                return r, f"OS {r.get('id')} (o token não lê o cadastro de clientes)"
        if len(regs) < 30:
            break
    raise ErroIxc("PARAR: o token não tem permissão para ler Clientes e não achei uma OS anterior deste cliente no NOC para copiar o endereço. Peça ao administrador do IXC para liberar a leitura de Clientes no token.")


def corpo_abertura(ixc: Ixc, p: dict, colaborador_id: str) -> dict:
    corpo = {
        "tipo": "C",
        "id_cliente": p["cliente"],
        "id_contrato_kit": p["contrato"],
        "id_assunto": p["assunto"],
        "id_filial": FILIAL_NOC,
        "setor": SETOR_NOC,
        "id_tecnico": colaborador_id,
        "prioridade": "N",
        "origem_endereco": "M",
        "origem_os_aberta": "M",
        "status": "A",
        "mensagem": p["descricao"],
        "data_abertura": agora_br(),
    }
    try:
        cls, _ = ixc.listar("cliente", "id", p["cliente"], rp=1)
        cls = [c for c in cls if str(c.get("id")) == p["cliente"]]
        if not cls:
            raise ErroIxc(f"PARAR: não achei o cliente {p['cliente']} no IXC")
        cl, origem = cls[0], "cadastro do cliente"
    except ErroIxc as e:
        if "permiss" not in norm(str(e)).replace("ã", "a").replace("ç", "c"):
            raise
        cl, origem = _endereco_da_ultima_os(ixc, p["cliente"])
    for k in CAMPOS_ENDERECO:
        if str(cl.get(k) or "").strip():
            corpo[k] = str(cl[k]).strip()
    cidade = str(cl.get("cidade") or cl.get("id_cidade") or "").strip()
    if cidade not in ("", "0"):
        corpo["id_cidade"] = cidade
    ixc.origem_endereco = origem
    return corpo


def abrir_os(ixc: Ixc, designacao: str, chamado: str, motivo: str, colaborador: str, gravar: bool = False) -> str:
    p = preparar(ixc, designacao, chamado, motivo)
    if p["avisos"]:
        raise ErroIxc("PARAR: não vou abrir a OS com pendências:\n" + "\n".join(f"• {a}" for a in p["avisos"]))
    cid, nome = achar_colaborador(ixc, colaborador)
    corpo = corpo_abertura(ixc, p, cid)
    visivel = {k: v for k, v in corpo.items() if k not in CAMPOS_ENDERECO and k != "id_cidade"}
    ends = [k for k in CAMPOS_ENDERECO + ("id_cidade",) if k in corpo]
    resumo = [f"Colaborador responsável: id {cid} - {nome}", f"Contrato: {p['contrato_nome']}", "Campos: " + ", ".join(f"{k}={v!r}" for k, v in visivel.items() if k not in ("mensagem",)),
              f"Endereço (copiado de: {getattr(ixc, 'origem_endereco', 'cadastro do cliente')}; valores não exibidos): {', '.join(ends) or 'nenhum campo preenchido'}", "Descrição:", p["descricao"]]
    if not gravar:
        return "\n".join(["📝 SIMULAÇÃO: nada foi gravado no IXC. Para abrir de verdade, rode de novo com --gravar (só depois do OK do humano)."] + resumo)
    resp = ixc.enviar("su_oss_chamado", corpo)
    novo = str(resp.get("id") or "").strip()
    if not novo.isdigit():
        raise ErroIxc("O IXC não devolveu o ID da OS. NÃO repita: confira no IXC se a OS foi aberta (procure pela designação) antes de qualquer nova tentativa.")
    lido, _ = ixc.listar("su_oss_chamado", "id", novo, rp=1)
    lido = [r for r in lido if str(r.get("id")) == novo]
    if not lido:
        return f"🔔 ID DA OS: {novo}\n⚠️ O IXC confirmou a gravação, mas não consegui reler a OS para conferir."
    r = lido[0]
    dif = [k for k in ("id_cliente", "id_assunto", "id_filial", "id_tecnico", "prioridade", "status", "mensagem") if str(r.get(k, "")).replace("\r\n", "\n").strip() != str(corpo[k]).strip()]
    if str(r.get("setor") or r.get("id_setor") or "") != SETOR_NOC:
        dif.append("setor")
    if contrato_da_os(r) != p["contrato"]:
        dif.append("contrato")
    saida = [f"🔔 ID DA OS: {novo}", f"Protocolo: {r.get('protocolo')}  |  Status: {r.get('status')}"] + resumo[:2]
    if dif:
        saida.append("⚠️ Conferir no IXC (o que foi lido difere do enviado): " + ", ".join(dif))
    else:
        saida.append("✅ Conferido: a OS foi lida de volta e bate com o que foi enviado.")
    return "\n".join(saida)


def executar_os(ixc: Ixc, os_id: str, mensagem: str, colaborador: str = "", gravar: bool = False) -> str:
    os_id = str(os_id).strip()
    if not os_id.isdigit():
        raise ErroIxc("informe o número da OS")
    mensagem = (mensagem or "").strip()
    if not mensagem:
        raise ErroIxc("a mensagem não pode ficar vazia")
    r = ler_os(ixc, os_id)
    if str(r.get("setor") or r.get("id_setor") or "") != SETOR_NOC or str(r.get("id_assunto")) != ASSUNTO_GERAL:
        raise ErroIxc(f"PARAR: a OS {os_id} não é uma OS do NOC (setor {SETOR_NOC}, assunto {ASSUNTO_GERAL}). Não executo.")
    if r.get("status") == "F":
        raise ErroIxc(f"PARAR: a OS {os_id} já está finalizada.")
    if str(r.get("data_hora_execucao") or ZERO_DATA) != ZERO_DATA:
        raise ErroIxc(f"PARAR: a OS {os_id} já foi executada ({r.get('data_hora_execucao')}). Não executo de novo.")
    corpo = {"id_chamado": os_id, "mensagem": mensagem, "status": "EX", "data_inicio": agora_br()}
    quem = ""
    if str(colaborador).strip():
        cid, nome = achar_colaborador(ixc, colaborador)
        corpo["id_tecnico"] = cid
        quem = f" (colaborador id {cid} - {nome})"
    if not gravar:
        return f"📝 SIMULAÇÃO: nada foi gravado. Executaria a OS {os_id}{quem} com a mensagem: {mensagem!r}. Para executar de verdade, rode de novo com --gravar (só depois do OK do humano)."
    ixc.enviar("su_oss_chamado_executar", corpo)
    depois = ler_os(ixc, os_id)
    ok = str(depois.get("data_hora_execucao") or ZERO_DATA) != ZERO_DATA or depois.get("status") == "EX"
    if ok:
        return f"✅ OS {os_id} executada{quem}. Mensagem enviada: {mensagem!r}. Status agora: {depois.get('status')}."
    return f"⚠️ O IXC aceitou o envio, mas a OS {os_id} não aparece como executada (status {depois.get('status')}). Confira na tela antes de repetir."


def funcionarios(ixc: Ixc, nome: str) -> str:
    """Lista id e nome de funcionários (só esses dois campos)."""
    regs, _ = ixc.listar("funcionarios", "funcionario", nome.strip(), rp=20, oper="L")
    alvo = norm(nome)
    linhas = []
    for r in regs:
        n = str(r.get("funcionario", "")).strip()
        if alvo and alvo not in norm(n):
            continue
        linhas.append(f"id {r.get('id')} - {n}")
    if not linhas:
        return f"Nenhum funcionário encontrado para '{nome}'."
    return "\n".join(linhas)


def principal(argv=None) -> int:
    ap = argparse.ArgumentParser(description="NOC: prepara, abre e executa OS no IXC (simula por padrão; grava só com --gravar)")
    ap.add_argument("--designacao", default="")
    ap.add_argument("--comparar", nargs=2, metavar=("OS_A", "OS_B"))
    ap.add_argument("--mostrar-iguais", action="store_true", help="com --comparar: mostra também os valores curtos dos campos iguais")
    ap.add_argument("--chamado", default="")
    ap.add_argument("--motivo", default="")
    ap.add_argument("--descobrir", action="store_true")
    ap.add_argument("--funcionarios", metavar="NOME", help="lista id e nome de funcionários pelo nome")
    ap.add_argument("--abrir", action="store_true", help="abre a OS (simulação, a menos que use --gravar)")
    ap.add_argument("--executar-os", metavar="OS", help="Ações > Executar na OS (simulação, a menos que use --gravar)")
    ap.add_argument("--mensagem", default=MSG_EXECUTAR)
    ap.add_argument("--colaborador", default="", help="id do colaborador responsável (veja --funcionarios)")
    ap.add_argument("--gravar", action="store_true", help="grava de verdade no IXC (só depois do OK do humano)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        url, token, _ = acesso_ixc()
        ixc = Ixc(url, token)
        if a.funcionarios:
            print(funcionarios(ixc, a.funcionarios))
            return 0
        if a.executar_os:
            print(executar_os(ixc, a.executar_os, a.mensagem, a.colaborador, a.gravar))
            return 0
        if a.abrir:
            print(abrir_os(ixc, a.designacao, a.chamado, a.motivo, a.colaborador, a.gravar))
            return 0
        if a.comparar:
            print(comparar(ixc, *a.comparar, iguais_valores=a.mostrar_iguais))
            return 0
        if not a.designacao.strip():
            raise ErroIxc("informe --designacao (ou --comparar OS_A OS_B)")
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
