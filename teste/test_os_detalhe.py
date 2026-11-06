import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "os-detalhe"))
import os_detalhe as m  # noqa: E402

TOKEN = "184:abcdef0123456789abcdef0123456789"

OSS = [
    {"id": "76580", "status": "F", "id_assunto": "135", "id_tecnico": "184", "prioridade": "B", "id_cliente": "150", "id_contrato_kit": "7386",
     "data_abertura": "2026-11-06 09:41:27", "data_hora_assumido": "0000-00-00 00:00:00", "data_hora_execucao": "2026-11-06 11:47:36",
     "data_fechamento": "2026-11-06 12:14:50", "endereco": "Rua Secreta", "numero": "99", "bairro": "Centro", "cep": "57000-000", "id_cidade": "1695", "telefone": "82999990000", "email": "x@y.com",
     "mensagem": "Designação / Vlan: SDR BRM 83104884 - Chamado interno: OEMP-42798\r\n", "mensagem_resposta": "Pendencia Cliente: Validação cliente\r\n"},
    {"id": "76581", "status": "A", "id_assunto": "55", "id_tecnico": "114", "prioridade": "N", "id_cliente": "150", "id_contrato_kit": "8054",
     "data_abertura": "2026-11-06 10:00:00", "data_hora_assumido": "0000-00-00 00:00:00", "data_hora_execucao": "0000-00-00 00:00:00",
     "data_fechamento": "0000-00-00 00:00:00", "mensagem": "Designação / Vlan: SDR TAF 83108054\nMotivo: Inoperante", "mensagem_resposta": ""},
    {"id": "76400", "status": "EX", "id_assunto": "55", "id_tecnico": "114", "prioridade": "N", "id_cliente": "150", "id_contrato_kit": "8054",
     "data_abertura": "2026-11-04 10:00:00", "data_hora_assumido": "0000-00-00 00:00:00", "data_hora_execucao": "2026-11-04 11:00:00",
     "data_fechamento": "0000-00-00 00:00:00", "mensagem": "Designação / Vlan: SDR TAF 83108054\nMotivo: Lento", "mensagem_resposta": ""},
]
HIST = [{"id": str(i), "id_chamado": "76580", "mensagem": f"atualização {i}", "data": f"2026-11-06 1{i}:00:00", "id_usuarios": "184"} for i in range(1, 8)]


class Fake(BaseHTTPRequestHandler):
    permitir_historico = True
    permitir_cliente = True
    chamadas = []

    def log_message(self, *a):
        pass

    def do_POST(self):
        corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode())
        Fake.chamadas.append((self.command, self.path, self.headers.get("ixcsoft"), corpo))
        tabela = self.path.strip("/").split("/")[-1]
        qt, valor, oper = corpo["qtype"].split(".")[-1], corpo["query"], corpo["oper"]
        if tabela == "su_oss_chamado":
            regs = [r for r in OSS if (valor.lower() in r.get(qt, "").lower() if oper == "L" else r.get(qt) == valor)]
            regs.sort(key=lambda r: int(r["id"]), reverse=corpo.get("sortorder") == "desc")
        elif tabela == "su_oss_chamado_mensagem":
            if not Fake.permitir_historico:
                return self._json({"type": "error", "message": "Você não tem permissão para acessar o recurso"})
            regs = sorted([h for h in HIST if h["id_chamado"] == valor], key=lambda h: int(h["id"]), reverse=corpo.get("sortorder") == "desc")
        elif tabela == "cliente":
            if not Fake.permitir_cliente:
                return self._json({"type": "error", "message": "Você não tem permissão para acessar o recurso"})
            regs = [{"id": "150", "razao": "Oi Móvel S.A", "fantasia": "Oi", "cnpj_cpf": "00.000.000/0001-00", "telefone_celular": "82999990000"}] if valor == "150" else []
        elif tabela == "cliente_contrato":
            regs = [{"id": "7386", "contrato": "7386 - Vídeo Polícia BPRV-059 - L2L", "descricao_aux_plano_venda": "SDR IMJ 83107386", "status": "A"}] if valor == "7386" else []
        elif tabela == "cidade":
            regs = [{"id": "1695", "nome": "Maceió"}] if valor == "1695" else []
        elif tabela == "su_oss_assunto":
            regs = [{"id": "135", "assunto": "Reparo Incidentes"}] if valor == "135" else []
        else:
            return self._json({"type": "error", "message": "Recurso não está disponível!"})
        n = int(corpo["rp"])
        self._json({"page": "1", "total": str(len(regs)), "registros": regs[:n]})

    def _json(self, d):
        b = json.dumps(d).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


@pytest.fixture()
def servidor():
    Fake.permitir_historico = True
    Fake.permitir_cliente = True
    Fake.chamadas = []
    s = HTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    yield {"IXC_URL": f"http://127.0.0.1:{s.server_address[1]}", "IXC_TOKEN": TOKEN}
    s.shutdown()


def rodar(capsys, env, *args):
    cod = m.principal(list(args), env=env)
    cap = capsys.readouterr()
    return cod, cap.out, cap.err


def test_detalhe_com_historico(capsys, servidor):
    cod, out, err = rodar(capsys, servidor, "--os", "76580", "--ultimas", "3")
    assert cod == 0 and err == ""
    assert "O.S. 76580" in out and "Status: Finalizada" in out and "Reparo Incidentes" in out and "Responsável: Jennypher" in out
    assert "Prioridade: Baixa" in out and "Aberta em: 06/11/2026 09:41" in out and "Assumida em: -" in out
    assert "SDR BRM 83104884" in out and "Pendencia Cliente: Validação cliente" in out
    assert "Últimas 3 atualizações" in out and "atualização 7" in out and "atualização 5" in out and "atualização 4" not in out
    assert out.index("atualização 7") < out.index("atualização 6")  # mais recente primeiro


def test_sem_permissao_no_historico_segue_com_os_campos(capsys, servidor):
    Fake.permitir_historico = False
    cod, out, err = rodar(capsys, servidor, "--os", "76580")
    assert cod == 0
    assert "Aviso: histórico completo indisponível" in out and "Você não tem permissão" in out
    assert "Pendencia Cliente" in out  # campos da O.S. continuam


def test_cliente_contrato_e_local(capsys, servidor):
    cod, out, err = rodar(capsys, servidor, "--os", "76580")
    assert "Cliente: Oi Móvel S.A (Oi) [id 150]" in out
    assert "Contrato: 7386 - Vídeo Polícia BPRV-059 - L2L [id 7386] | SDR IMJ 83107386 | status do contrato A" in out
    assert "Local da O.S.: Rua Secreta, 99, Centro, Maceió - CEP 57000-000" in out


def test_nunca_imprime_telefone_email_documento_nem_token(capsys, servidor):
    cod, out, err = rodar(capsys, servidor, "--os", "76580")
    for segredo in ("82999990000", "x@y.com", "00.000.000/0001-00", TOKEN):
        assert segredo not in out + err


def test_sem_permissao_em_clientes_mostra_id_e_segue(capsys, servidor):
    Fake.permitir_cliente = False
    cod, out, err = rodar(capsys, servidor, "--os", "76580")
    assert cod == 0 and "Cliente: id 150 (nome indisponível" in out and "Pendencia Cliente" in out


def test_busca_unica_mostra_detalhe_e_varias_lista(capsys, servidor):
    cod, out, _ = rodar(capsys, servidor, "--buscar", "SDR BRM 83104884")
    assert cod == 0 and out.startswith("O.S. 76580")
    cod, out, _ = rodar(capsys, servidor, "--buscar", "SDR TAF 83108054")
    assert "Encontrei 2 O.S." in out and out.index("76581") < out.index("76400") and "Diga qual número" in out
    cod, out, _ = rodar(capsys, servidor, "--buscar", "8054", "--por", "contrato")
    assert "Encontrei 2 O.S." in out
    cod, out, _ = rodar(capsys, servidor, "--buscar", "NADA EXISTE")
    assert cod == 0 and "Nenhuma O.S." in out


def test_erros(capsys, servidor):
    cod, out, err = rodar(capsys, servidor, "--os", "999")
    assert cod == 1 and "não encontrada" in err
    cod, out, err = rodar(capsys, servidor, "--os", "76580; DROP")
    assert cod == 1 and "só dígitos" in err
    cod, out, err = rodar(capsys, {"IXC_URL": "http://127.0.0.1:9", "IXC_TOKEN": TOKEN}, "--os", "76580")
    assert cod == 1 and TOKEN not in err


def test_somente_leitura(capsys, servidor):
    rodar(capsys, servidor, "--os", "76580")
    rodar(capsys, servidor, "--buscar", "SDR TAF 83108054")
    assert Fake.chamadas and all(c[0] == "POST" and c[2] == "listar" for c in Fake.chamadas)
    fonte = Path(m.__file__).read_text(encoding="utf-8")
    for proibido in ("PUT", "DELETE", "su_oss_chamado_executar", "su_oss_chamado_fechar", ".enviar("):
        assert proibido not in fonte, proibido


def test_testar_acesso(capsys, servidor):
    cod, out, _ = rodar(capsys, servidor, "--testar-acesso")
    assert cod == 0 and "acesso OK" in out and TOKEN not in out


def test_skill_detalhe_os_sem_frase_fixa_e_somente_leitura():
    s = (Path(m.__file__).parent / "skill-detalhe-os.md").read_text(encoding="utf-8")
    assert "A pessoa pode escrever de qualquer jeito" in s and "Não existe frase fixa" in s
    assert "SOMENTE LEITURA" in s and "NUNCA usar curl" in s and "Nunca invente" in s
    for flag in ("--os", "--buscar", "--por", "--ultimas"):
        assert flag in s
