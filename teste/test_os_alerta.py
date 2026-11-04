import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "socorro"))
import os_alerta as m  # noqa: E402

AGORA = datetime(2026, 11, 3, 8, 0, 0)  # terça


def os_(i, horas, assunto="20", assumida=True, status="EN", tecnico=140):
    ab = (AGORA - timedelta(hours=horas)).strftime("%Y-%m-%d %H:%M:%S")
    return {"id": str(i), "id_tecnico": str(tecnico), "id_assunto": assunto, "data_abertura": ab, "status": status,
            "data_hora_assumido": ab if assumida else "0000-00-00 00:00:00",
            "nome_cliente": "SEGREDO", "endereco": "Rua Secreta", "mensagem": "texto privado"}


def salvar_paginas(tecnico, regs, por_pagina=30, total=None, pasta=None):
    """Simula o que o agente faz: uma resposta crua por página em os_<ID>_p<N>.json."""
    pasta = Path(pasta or tempfile.mkdtemp())
    total = len(regs) if total is None else total
    for n, i in enumerate(range(0, max(len(regs), 1), por_pagina), 1):
        (pasta / f"os_{tecnico}_p{n}.json").write_text(
            json.dumps({"page": str(n), "total": str(total), "registros": regs[i:i + por_pagina]}), encoding="utf-8")
    return str(pasta / f"os_{tecnico}_p*.json")


def rodar(capsys, argv, dados, agora=AGORA):
    entradas = []
    for tid, regs in dados.items():
        entradas += ["--entrada", f"{tid}={salvar_paginas(tid, regs)}"]
    cod = m.principal(argv + entradas, agora=agora)
    return cod, capsys.readouterr()


def test_bordas_e_regras():
    dados = [os_(1, 48), os_(2, 49), os_(3, 168), os_(4, 721), os_(5, 720), os_(6, 9999, assunto="278"), os_(7, 5, status="F")]
    g = m.classificar(m.abertas_de_registros(dados), AGORA)
    assert [x["id"] for x in g["recentes"]] == ["2"]          # 48 h exatas não é alerta; 49 h sim
    assert [x["id"] for x in g["atencao"]] == ["5", "3"]      # 168 h e 720 h ficam em atenção (mais antiga primeiro)
    assert [x["id"] for x in g["criticas"]] == ["4"]          # >720 h
    assert [x["id"] for x in g["pausadas"]] == ["6"]          # pausada fora do alerta


def test_so_f_e_fechada():
    abertas = m.abertas_de_registros([os_(1, 100), os_(2, 100, status="F"), os_(3, 100, status="C")])
    assert [r["id"] for r in abertas] == ["1", "3"]  # igual à skill: só F é fechada


def test_modo_gerente_formato_e_sem_dados_de_cliente(capsys):
    cod, out = rodar(capsys, ["--modo", "gerente", "--tecnicos", "140,121"],
                     {140: [os_(10, 24 * 40, "56"), os_(11, 3), os_(12, 100, "278")], 121: []})
    assert cod == 0
    t = out.out
    assert "👷 Milena — 3 abertas | 1 em alerta | 1 pausadas" in t
    assert "🔴 Mais de 30 dias (1)" in t and "• #10 · Ativação · 40 dias" in t
    assert "⏸ Pausadas (1)" in t and "Luiz Felipe" not in t  # técnico sem O.S. não aparece
    assert t.strip().endswith("📊 Total: 3 abertas, 1 em alerta, 1 pausadas")
    for proibido in ("SEGREDO", "Rua Secreta", "texto privado"):
        assert proibido not in t


def test_sem_nada_nao_imprime(capsys):
    cod, out = rodar(capsys, ["--modo", "gerente", "--tecnicos", "140"], {140: []})
    assert cod == 0 and out.out == "" and out.err == ""


def test_pessoal_destaques_e_limite(capsys):
    lista = [os_(i, 24 * (3 + i), "5", assumida=(i % 2 == 0), tecnico=121) for i in range(1, 16)] + [os_(99, 10, "278", tecnico=121)]
    cod, out = rodar(capsys, ["--modo", "pessoal", "--tecnico", "121", "--max-linhas", "5"], {121: lista})
    t = out.out
    assert "Bom dia, Luiz Felipe!" in t and "16 O.S. abertas (15 em alerta, 1 pausadas)" in t
    assert "🎯 Para dar atenção primeiro:" in t
    assert "A mais antiga: #15" in t and "15 são de Ativação de cliente" in t and "sem data de assumida" in t
    assert t.count("• #") <= 5 + 4 and "…e mais 10 O.S. em alerta" in t
    assert "⏸ Pausadas (1): #99" in t
    assert "SEGREDO" not in t


def test_so_dias_uteis(capsys):
    sabado = datetime(2026, 11, 7, 8, 0, 0)
    cod, out = rodar(capsys, ["--modo", "pessoal", "--tecnico", "140", "--so-dias-uteis"], {140: [os_(1, 100)]}, agora=sabado)
    assert cod == 0 and out.out == ""
    cod, out = rodar(capsys, ["--modo", "pessoal", "--tecnico", "140", "--so-dias-uteis"], {140: [os_(1, 100)]})
    assert out.out != ""


def test_json_sem_dados_de_cliente(capsys):
    cod, out = rodar(capsys, ["--modo", "pessoal", "--tecnico", "140", "--json"], {140: [os_(1, 100, assumida=False)]})
    dados = json.loads(out.out)
    assert dados[0]["abertas"] == 1 and dados[0]["destaques"]["nao_assumidas"] == 1
    assert "SEGREDO" not in out.out and "Rua Secreta" not in out.out


def test_assunto_desconhecido_mostra_o_id(capsys):
    cod, out = rodar(capsys, ["--modo", "gerente", "--tecnicos", "140"], {140: [os_(1, 100, "999")]})
    assert "assunto 999" in out.out


def test_divisao_nao_corta_linha():
    texto = "\n".join(f"• #{i} · Ativação de cliente · {i} dias" for i in range(400))
    partes = m.dividir(texto)
    assert len(partes) > 1 and all(len(p) <= m.LIMITE_TELEGRAM for p in partes)
    assert "\n".join(partes) == texto


# --- entrada: arquivos salvos pelo agente (uma página por arquivo, resposta crua) -----------------


def test_varias_paginas_com_curinga_igual_a_um_arquivo(capsys):
    regs = [os_(i, 24 * i) for i in range(1, 71)]  # 70 O.S. -> 3 páginas de 30
    multi = salvar_paginas(140, regs, por_pagina=30)
    unico = salvar_paginas(140, regs, por_pagina=1000)
    assert len(list(Path(multi).parent.glob("os_140_p*.json"))) == 3
    saidas = []
    for padrao in (multi, unico):
        assert m.principal(["--modo", "gerente", "--tecnicos", "140", "--entrada", f"140={padrao}"], agora=AGORA) == 0
        saidas.append(capsys.readouterr().out)
    assert saidas[0] == saidas[1] and "70 abertas" in saidas[0]


def test_aceita_lista_de_paginas_em_um_arquivo_e_virgulas(tmp_path, capsys):
    regs = com = [os_(1, 100), os_(2, 100), os_(3, 100)]
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    a.write_text(json.dumps({"total": 3, "registros": regs[:2]}))
    b.write_text(json.dumps({"total": 3, "registros": regs[2:]}))
    assert m.principal(["--modo", "pessoal", "--tecnico", "140", "--entrada", f"{a},{b}"], agora=AGORA) == 0
    assert "3 O.S. abertas" in capsys.readouterr().out


def test_pagina_repetida_nao_conta_em_dobro(tmp_path, capsys):
    regs = [os_(1, 100), os_(2, 100)]
    (tmp_path / "os_140_p1.json").write_text(json.dumps({"total": 2, "registros": regs}))
    (tmp_path / "os_140_p1_copia.json").write_text(json.dumps({"total": 2, "registros": regs}))
    assert m.principal(["--modo", "pessoal", "--tecnico", "140", "--entrada", str(tmp_path / "os_140_p1*.json")], agora=AGORA) == 0
    assert "2 O.S. abertas" in capsys.readouterr().out


def test_total_do_ixc_e_conferido(capsys):
    regs = [os_(i, 100) for i in range(1, 4)]
    padrao = salvar_paginas(140, regs, total=5)  # IXC disse 5, só 3 foram salvas
    assert m.principal(["--modo", "pessoal", "--tecnico", "140", "--entrada", padrao], agora=AGORA) == 1
    assert "incompleta para o técnico 140: 3 O.S. lidas e o IXC informou 5" in capsys.readouterr().err


def test_arquivo_de_outro_tecnico_e_recusado(capsys):
    padrao = salvar_paginas(140, [os_(1, 100, tecnico=161)])
    assert m.principal(["--modo", "pessoal", "--tecnico", "140", "--entrada", padrao], agora=AGORA) == 1
    assert "outro técnico" in capsys.readouterr().err


def test_arquivo_ruim_ou_ausente(tmp_path, capsys):
    ruim = tmp_path / "os_140_p1.json"
    ruim.write_text("não é json")
    assert m.principal(["--modo", "pessoal", "--tecnico", "140", "--entrada", str(ruim)], agora=AGORA) == 1
    assert "não consegui ler" in capsys.readouterr().err
    assert m.principal(["--modo", "pessoal", "--tecnico", "140", "--entrada", str(tmp_path / "nada_*.json")], agora=AGORA) == 1
    assert "nenhum arquivo encontrado" in capsys.readouterr().err


def test_resposta_real_do_ixc_com_70_campos(capsys):
    """A resposta crua traz dezenas de campos (cliente, endereço...): só 5 são usados e nada vaza."""
    r = os_(1, 24 * 40)
    r.update({f"campo_{i}": f"valor{i}" for i in range(60)} | {"id_cliente": "123456", "latitude": "-12.9", "telefone": "7199999999"})
    padrao = salvar_paginas(140, [r])
    assert m.principal(["--modo", "gerente", "--tecnicos", "140", "--entrada", f"140={padrao}"], agora=AGORA) == 0
    t = capsys.readouterr().out
    for proibido in ("123456", "-12.9", "7199999999", "valor3", "SEGREDO"):
        assert proibido not in t


# --- O script consulta o IXC sozinho (servidor simulado) ------------------------------------------

TOKEN = "9:SEGREDOXYZ"


class FakeIxc:
    """IXC simulado: guarda o que recebeu, pagina de 30, devolve total e valida o Basic auth."""

    def __init__(self, os_por_tecnico, assuntos=None, erro=None):
        self.os = os_por_tecnico
        self.assuntos = assuntos or {}
        self.erro = erro
        self.pedidos = []
        fake = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                fake.pedidos.append((self.path, dict(self.headers), corpo))
                import base64
                if self.headers.get("Authorization") != "Basic " + base64.b64encode(TOKEN.encode()).decode():
                    return self._r(401, {"message": "nao autorizado"})
                if fake.erro:
                    return self._r(200, {"type": "error", "message": f"falha com {TOKEN}"})
                if self.path.endswith("/su_oss_chamado"):
                    regs = fake.os.get(int(corpo["query"]), [])
                    pg, rp = int(corpo["page"]), int(corpo["rp"])
                    return self._r(200, {"page": str(pg), "total": str(len(regs)), "registros": regs[(pg - 1) * rp: pg * rp]})
                if self.path.endswith("/su_oss_assunto"):
                    nome = fake.assuntos.get(corpo["query"])
                    return self._r(200, {"total": "1" if nome else "0", "registros": [{"id": corpo["query"], "assunto": nome}] if nome else []})
                self._r(404, {})

            def _r(self, cod, obj):
                b = json.dumps(obj).encode()
                self.send_response(cod)
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)

        self.srv = HTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.srv.server_port}/webservice/v1"
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def fechar(self):
        self.srv.shutdown()


def com_acesso(monkeypatch, fake, tmp_path=None):
    for k in ("IXC_URL", "IXC_TOKEN", "IXC_TOKEN_FILE", "IXC_COFRE"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("IXC_URL", fake.url)
    monkeypatch.setenv("IXC_TOKEN", TOKEN)


def test_script_consulta_o_ixc_sozinho_varias_paginas(monkeypatch, capsys):
    regs = [os_(i, 100 + i) for i in range(1, 71)]  # 70 O.S.: 3 páginas
    fake = FakeIxc({140: regs, 121: [os_(900, 100, tecnico=121)]}, assuntos={"20": "Vistoria Interna"})
    com_acesso(monkeypatch, fake)
    try:
        assert m.principal(["--modo", "gerente", "--tecnicos", "140,121"], agora=AGORA) == 0
    finally:
        fake.fechar()
    t = capsys.readouterr().out
    assert "Milena" in t and "70" in t and "SEGREDO" not in t and TOKEN not in t
    paginas = [c["page"] for p, h, c in fake.pedidos if p.endswith("su_oss_chamado") and c["query"] == "140"]
    assert paginas == ["1", "2", "3"]
    assert all({k.lower(): v for k, v in h.items()}.get("ixcsoft") == "listar" for _, h, _ in fake.pedidos)


def test_ixc_so_le_nunca_escreve_nem_apaga():
    fonte = Path(m.__file__).read_text(encoding="utf-8")
    assert "DELETE" not in fonte and "PUT" not in fonte and "inserir" not in fonte


def test_token_nunca_aparece_na_saida_nem_no_erro(monkeypatch, capsys):
    fake = FakeIxc({140: [os_(1, 100)]}, erro=True)
    com_acesso(monkeypatch, fake)
    try:
        assert m.principal(["--modo", "pessoal", "--tecnico", "140"], agora=AGORA) == 1
    finally:
        fake.fechar()
    cap = capsys.readouterr()
    assert TOKEN not in cap.out + cap.err and "SEGREDOXYZ" not in cap.out + cap.err and "[token]" in cap.err


def test_token_errado_da_erro_claro(monkeypatch, capsys):
    fake = FakeIxc({140: [os_(1, 100)]})
    com_acesso(monkeypatch, fake)
    monkeypatch.setenv("IXC_TOKEN", "1:outro")
    try:
        assert m.principal(["--modo", "pessoal", "--tecnico", "140"], agora=AGORA) == 1
    finally:
        fake.fechar()
    assert "IXC respondeu 401" in capsys.readouterr().err


def test_sem_acesso_diz_o_que_falta(monkeypatch, capsys, tmp_path):
    for k in ("IXC_URL", "IXC_TOKEN", "IXC_TOKEN_FILE"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("IXC_COFRE", str(tmp_path / "nao-existe.json"))
    monkeypatch.setattr(m.os.path, "abspath", lambda p: str(tmp_path / "x.py"))
    assert m.principal(["--modo", "pessoal", "--tecnico", "140"], agora=AGORA) == 1
    assert "sem acesso ao IXC" in capsys.readouterr().err


def test_acesso_pelo_cofre_do_agente(monkeypatch, tmp_path):
    for k in ("IXC_URL", "IXC_TOKEN", "IXC_TOKEN_FILE"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(m.os.path, "abspath", lambda p: str(tmp_path / "x.py"))
    cofre = tmp_path / "cofre-chaves.json"
    cofre.write_text(json.dumps({"OUTRA": {"valor": "x", "tipo": "bearer"},
                                 "ixc-webfoco": {"valor": TOKEN, "tipo": "ixc", "base_url": "https://host/webservice/v1", "guardada_em": "2026"}}))
    monkeypatch.setenv("IXC_COFRE", str(cofre))
    assert m.acesso_ixc() == ("https://host/webservice/v1", TOKEN, "cofre do agente")
    cofre.write_text(json.dumps({"IXC": {"valor": "1:nome", "tipo": "ixc"}, "ixc-webfoco": {"valor": TOKEN, "tipo": "ixc"}}))
    assert m.acesso_ixc()[1] == "1:nome"  # a entrada chamada "IXC" vence


def test_acesso_por_arquivo_exige_chmod_600(monkeypatch, tmp_path):
    monkeypatch.delenv("IXC_TOKEN", raising=False)
    f = tmp_path / "acesso.json"
    f.write_text(json.dumps({"url": "https://h/v1", "token": TOKEN}))
    monkeypatch.setenv("IXC_TOKEN_FILE", str(f))
    os.chmod(f, 0o644)
    try:
        m.acesso_ixc()
        assert False
    except m.ErroIxc as e:
        assert "chmod 600" in str(e) and TOKEN not in str(e)
    os.chmod(f, 0o600)
    assert m.acesso_ixc() == ("https://h/v1", TOKEN, "arquivo (IXC_TOKEN_FILE)")


def test_testar_acesso(monkeypatch, capsys):
    fake = FakeIxc({}, assuntos={"278": "Pausado/Congelado"})
    com_acesso(monkeypatch, fake)
    try:
        assert m.principal(["--testar-acesso"]) == 0
    finally:
        fake.fechar()
    out = capsys.readouterr().out
    assert "acesso vindo de: ambiente" in out and "acesso OK" in out and TOKEN not in out


def test_assunto_novo_e_buscado_no_ixc(monkeypatch, capsys):
    fake = FakeIxc({140: [os_(1, 24 * 40, assunto="999")]}, assuntos={"999": "Assunto Novo X"})
    com_acesso(monkeypatch, fake)
    try:
        assert m.principal(["--modo", "pessoal", "--tecnico", "140"], agora=AGORA) == 0
    finally:
        fake.fechar()
        m.ASSUNTOS.pop("999", None)
    assert "Assunto Novo X" in capsys.readouterr().out


def test_ixc_devolve_os_de_outro_tecnico_e_recusado(monkeypatch, capsys):
    fake = FakeIxc({140: [os_(1, 100, tecnico=161)]})
    com_acesso(monkeypatch, fake)
    try:
        assert m.principal(["--modo", "pessoal", "--tecnico", "140"], agora=AGORA) == 1
    finally:
        fake.fechar()
    assert "outro técnico" in capsys.readouterr().err


def test_sem_os_abertas_nao_imprime_nada(monkeypatch, capsys):
    fake = FakeIxc({140: [os_(1, 100, status="F")]})
    com_acesso(monkeypatch, fake)
    try:
        assert m.principal(["--modo", "pessoal", "--tecnico", "140"], agora=AGORA) == 0
    finally:
        fake.fechar()
    assert capsys.readouterr().out == ""
