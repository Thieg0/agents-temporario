import base64
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "noc"))
import preparar_os as m  # noqa: E402

TOKEN = "9:SEGREDOXYZ"
DES = "SDR TAF 83108054"
CONTRATO = "8054 - Video Policia -SEAP-I-078 - Teixeira de Freitas - Rua Nova 123"


def os_(i, contrato="8054", msg=None, cliente="150"):
    return {"id": str(i), "id_contrato": contrato, "id_cliente": cliente, "status": "F",
            "mensagem": msg or f"Designação / Vlan:{DES}\nCliente Final: SEAP-I-078", "telefone_contato": "7199999999", "endereco": "Rua Secreta"}


class Fake:
    def __init__(self, oss, contrato=None, erro=False):
        self.oss, self.pedidos, self.erro = oss, [], erro
        self.contrato = {"id": "8054", "id_cliente": "150", "contrato": CONTRATO, "status": "A",
                         "descricao_aux_plano_venda": f"OI: TAF 5043307 WT: {DES}"} if contrato is None else contrato
        f = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                c = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                f.pedidos.append((self.path, dict(self.headers), c))
                if self.headers.get("Authorization") != "Basic " + base64.b64encode(TOKEN.encode()).decode():
                    return self._r(401, {})
                if f.erro:
                    return self._r(200, {"type": "error", "message": f"falha {TOKEN}"})
                if self.path.endswith("/su_oss_chamado"):
                    regs = f.oss
                    if c.get("qtype") == "su_oss_chamado.id":
                        regs = [r for r in f.oss if r["id"] == c["query"]]
                    return self._r(200, {"total": str(len(regs)), "registros": regs})
                if self.path.endswith("/cliente_contrato"):
                    return self._r(200, {"total": "1", "registros": [f.contrato] if f.contrato else []})
                if self.path.endswith("/funcionarios"):
                    todos = [{"id": "184", "funcionario": "Maria Souza", "cpf_cnpj": "111.222.333-44", "fone_celular": "7188887777"},
                             {"id": "185", "funcionario": "Pedro Lima", "cpf_cnpj": "999"}]
                    return self._r(200, {"total": "2", "registros": todos})
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


def rodar(monkeypatch, capsys, fake, args):
    for k in ("IXC_TOKEN_FILE", "IXC_COFRE"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("IXC_URL", fake.url)
    monkeypatch.setenv("IXC_TOKEN", TOKEN)
    try:
        cod = m.principal(args)
    finally:
        fake.srv.shutdown()
    c = capsys.readouterr()
    return cod, c.out, c.err


def test_caminho_feliz(monkeypatch, capsys):
    f = Fake([os_(75811), os_(73546), os_(63524)])
    cod, out, err = rodar(monkeypatch, capsys, f, ["--designacao", DES, "--chamado", "OEMP-42074", "--motivo", "Inoperante"])
    assert cod == 0 and err == ""
    assert "Designação / Vlan: SDR TAF 83108054\nCliente Final: Video Policia -SEAP-I-078\nChamado interno: OEMP-42074\nMotivo do chamado: Inoperante" in out
    assert "Assunto: 55 (Geral)" in out and "Contrato: 8054" in out and "Cliente: 150" in out
    assert "OS 75811 (a mais recente finalizada; 3 OS" in out and "nada foi gravado" in out
    assert "⚠️" not in out
    for proibido in ("7199999999", "Rua Secreta", "Rua Nova", TOKEN):
        assert proibido not in out


def test_so_le_nunca_escreve(monkeypatch, capsys):
    f = Fake([os_(1)])
    rodar(monkeypatch, capsys, f, ["--designacao", DES, "--chamado", "x", "--motivo", "y"])
    assert f.pedidos and all({k.lower(): v for k, v in h.items()}["ixcsoft"] == "listar" for _, h, _ in f.pedidos)
    fonte = Path(m.__file__).read_text(encoding="utf-8")
    assert "DELETE" not in fonte and "PUT" not in fonte and "inserir" not in fonte


def test_busca_por_mensagem_com_like(monkeypatch, capsys):
    f = Fake([os_(1)])
    rodar(monkeypatch, capsys, f, ["--designacao", DES])
    p, _, c = f.pedidos[0]
    assert c["qtype"] == "su_oss_chamado.mensagem" and c["oper"] == "L" and c["query"] == DES and c["sortorder"] == "desc"


def test_designacao_com_outra_caixa_e_espacos(monkeypatch, capsys):
    f = Fake([os_(1, msg="designação / vlan:  sdr  taf 83108054 ")])
    cod, out, _ = rodar(monkeypatch, capsys, f, ["--designacao", DES, "--chamado", "a", "--motivo", "b"])
    assert cod == 0 and "OS 1 (" in out


def test_ignora_os_que_so_aparece_por_acaso(monkeypatch, capsys):
    f = Fake([os_(1, msg="outra coisa SDR TAF 99999999")])
    cod, _, err = rodar(monkeypatch, capsys, f, ["--designacao", DES])
    assert cod == 1 and "PARAR: nenhuma OS" in err


def test_sem_os_para(monkeypatch, capsys):
    cod, out, err = rodar(monkeypatch, capsys, Fake([]), ["--designacao", DES])
    assert cod == 1 and out == "" and "PARAR: nenhuma OS" in err


def test_contratos_diferentes_param(monkeypatch, capsys):
    f = Fake([os_(75811, "8054"), os_(63524, "7001")])
    cod, out, err = rodar(monkeypatch, capsys, f, ["--designacao", DES])
    assert cod == 1 and out == "" and "único contrato" in err and "OS 63524 (contrato 7001)" in err


def test_contrato_inexistente_para(monkeypatch, capsys):
    cod, _, err = rodar(monkeypatch, capsys, Fake([os_(1)], contrato={}), ["--designacao", DES])
    assert cod == 1 and "não achei o contrato 8054" in err


def test_avisos_contrato_inativo_e_designacao_ausente(monkeypatch, capsys):
    ct = {"id": "8054", "contrato": CONTRATO, "status": "I", "descricao_aux_plano_venda": "OI: TAF 5043307"}
    cod, out, _ = rodar(monkeypatch, capsys, Fake([os_(1)], contrato=ct), ["--designacao", DES, "--chamado", "a", "--motivo", "b"])
    assert cod == 0 and "status 'I'" in out and "designação não aparece" in out


def test_falta_chamado_e_motivo(monkeypatch, capsys):
    cod, out, _ = rodar(monkeypatch, capsys, Fake([os_(1)]), ["--designacao", DES])
    assert cod == 0 and "Chamado interno: [preencher]" in out and "faltou o chamado interno" in out and "faltou o motivo" in out


def test_cliente_final_formatos():
    f = m.cliente_final
    assert f("8054 - Video Policia -SEAP-I-078 - Teixeira de Freitas - X") == "Video Policia -SEAP-I-078"
    assert f("8054 - Video Policia -SEAP-I-078- Teixeira") is None or f("8054 - Video Policia -SEAP-I-078- Teixeira")
    assert f("sem formato nenhum") is None
    assert f("") is None and f(None) is None


def test_contrato_fora_do_formato_pede_preenchimento(monkeypatch, capsys):
    ct = {"id": "8054", "contrato": "contrato estranho", "status": "A", "descricao_aux_plano_venda": DES}
    cod, out, _ = rodar(monkeypatch, capsys, Fake([os_(1)], contrato=ct), ["--designacao", DES, "--chamado", "a", "--motivo", "b"])
    assert cod == 0 and "Cliente Final: [preencher]" in out and "não consegui tirar o Cliente Final" in out


def test_token_nunca_vaza_em_erro(monkeypatch, capsys):
    cod, out, err = rodar(monkeypatch, capsys, Fake([os_(1)], erro=True), ["--designacao", DES])
    assert cod == 1 and TOKEN not in out + err and "[token]" in err


def test_json(monkeypatch, capsys):
    cod, out, _ = rodar(monkeypatch, capsys, Fake([os_(75811)]), ["--designacao", DES, "--chamado", "a", "--motivo", "b", "--json"])
    d = json.loads(out)
    assert cod == 0 and d["os_modelo"] == "75811" and d["assunto"] == "55" and d["contrato"] == "8054" and d["cliente"] == "150"


def test_descobrir_mostra_nomes_sem_dados(monkeypatch, capsys):
    cod, out, _ = rodar(monkeypatch, capsys, Fake([os_(75811)]), ["--designacao", DES, "--descobrir"])
    assert cod == 0 and "id_contrato" in out and "telefone_contato" in out
    for proibido in ("7199999999", "Rua Secreta", "Rua Nova"):
        assert proibido not in out
    assert "id_contrato = '8054'" in out


def test_os_aberta_com_a_mesma_designacao_avisa_duplicada(monkeypatch, capsys):
    aberta = os_(76196)
    aberta["status"] = "A"
    cod, out, _ = rodar(monkeypatch, capsys, Fake([aberta, os_(75811), os_(73546)]), ["--designacao", DES, "--chamado", "a", "--motivo", "b"])
    assert cod == 0 and "JÁ EXISTE OS ABERTA" in out and "76196" in out and "Base: OS 75811" in out


def test_so_os_aberta_usa_ela_com_aviso(monkeypatch, capsys):
    aberta = os_(76196)
    aberta["status"] = "A"
    cod, out, _ = rodar(monkeypatch, capsys, Fake([aberta]), ["--designacao", DES, "--chamado", "a", "--motivo", "b"])
    assert cod == 0 and "nenhuma OS finalizada" in out and "JÁ EXISTE OS ABERTA" in out


def test_comparar_mostra_so_o_que_difere(monkeypatch, capsys):
    a, b = os_(75811), os_(76196)
    a["id_assunto"], b["id_assunto"] = "104", "55"
    a["status"], b["status"] = "F", "A"
    cod, out, _ = rodar(monkeypatch, capsys, Fake([a, b]), ["--comparar", "75811", "76196"])
    assert cod == 0 and "id_assunto: '104' | '55'" in out and "status: 'F' | 'A'" in out
    assert "id: '75811' | '76196'" in out and "id_cliente" not in out
    for proibido in ("7199999999", "telefone_contato", TOKEN):
        assert proibido not in out


def test_comparar_os_inexistente(monkeypatch, capsys):
    cod, _, err = rodar(monkeypatch, capsys, Fake([os_(1)]), ["--comparar", "1", "999"])
    assert cod == 1 and "não achei a OS 999" in err


def test_sem_designacao_nem_comparar(monkeypatch, capsys):
    cod, _, err = rodar(monkeypatch, capsys, Fake([os_(1)]), [])
    assert cod == 1 and "informe --designacao" in err


def test_comparar_mostrar_iguais(monkeypatch, capsys):
    a, b = os_(75811), os_(76196)
    a["prioridade"] = b["prioridade"] = "N"
    a["endereco"], b["endereco"] = "Rua Secreta A", "Rua Secreta B"
    cod, out, _ = rodar(monkeypatch, capsys, Fake([a, b]), ["--comparar", "75811", "76196", "--mostrar-iguais"])
    assert cod == 0 and "prioridade='N'" in out and "id_contrato='8054'" in out
    assert "7199999999" not in out and "telefone" not in out


def test_funcionarios_lista_id_e_nome_sem_dados_pessoais(monkeypatch, capsys):
    f = Fake([])
    cod, out, _ = rodar(monkeypatch, capsys, f, ["--funcionarios", "maria"])
    assert cod == 0 and "id 184 - Maria Souza" in out and "Pedro" not in out
    for proibido in ("111.222", "7188887777"):
        assert proibido not in out
    assert all(p[0].endswith("/funcionarios") for p in f.pedidos)


def test_funcionarios_sem_resultado(monkeypatch, capsys):
    cod, out, _ = rodar(monkeypatch, capsys, Fake([]), ["--funcionarios", "zzz"])
    assert cod == 0 and "Nenhum funcionário" in out
