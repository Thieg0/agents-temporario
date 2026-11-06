import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
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
    extras = []
    chamadas = []

    def log_message(self, *a):
        pass

    def do_POST(self):
        corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode())
        Fake.chamadas.append((self.command, self.path, self.headers.get("ixcsoft"), corpo))
        tabela = self.path.strip("/").split("/")[-1]
        qt, valor, oper = corpo["qtype"].split(".")[-1], corpo["query"], corpo["oper"]
        if tabela == "su_oss_chamado":
            regs = [r for r in OSS + Fake.extras if (valor.lower() in r.get(qt, "").lower() if oper == "L" else r.get(qt) == valor)]
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
        n, pg = int(corpo["rp"]), int(corpo.get("page", "1"))
        self._json({"page": str(pg), "total": str(len(regs)), "registros": regs[(pg - 1) * n:pg * n]})

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
    Fake.extras = []
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


AGORA = datetime(2026, 11, 9, 8, 0, 0)  # segunda-feira


def os_t(i, tecnico, dias, status="EN", assunto="55", campo="ultima_atualizacao"):
    d = (AGORA.replace(hour=8) - __import__("datetime").timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")
    return {"id": str(i), "id_tecnico": str(tecnico), "status": status, "id_assunto": assunto, "id_cliente": "150", "id_contrato_kit": "7386",
            "data_abertura": "2026-10-01 08:00:00", campo: d, "mensagem": f"mensagem da {i}\nsegunda linha", "mensagem_resposta": ""}


def rodar_desat(capsys, env, *args, agora=AGORA):
    cod = m.principal(["--desatualizadas", *args], env=env, agora=agora)
    cap = capsys.readouterr()
    return cod, cap.out, cap.err


def test_desatualizadas_regras(capsys, servidor):
    Fake.extras = [os_t(1, 121, 10), os_t(2, 121, 4), os_t(3, 121, 3), os_t(4, 121, 20, status="F"), os_t(5, 121, 20, assunto="278"),
                   os_t(6, 161, 30), os_t(7, 161, 1), os_t(8, 140, 50), os_t(9, 161, 8, status="C")]
    cod, out, err = rodar_desat(capsys, servidor, "--tecnicos", "121,161", "--dias", "3")
    assert cod == 0 and err == ""
    ids = [l.split(" | ")[0] for l in out.splitlines() if l.startswith("O.S. ") and " | " in l and not l.startswith("O.S. desatualizadas")]
    # 121: 1 (10 dias) e 2 (4 dias); 161: 6 (30 dias). Exatamente 3 dias (O.S. 3) e recentes não entram; F, C, pausada e outro técnico ficam fora
    assert ids == ["O.S. 1", "O.S. 2", "O.S. 6"], ids
    assert out.splitlines()[0].startswith("O.S. desatualizadas (Luiz Felipe, Edson): 3 sem atualização")
    assert "pausadas ignoradas: 1" in out and "Sem atualização há 10 dias" in out and "mensagem da 1 / segunda linha" in out


def test_desatualizadas_mostra_historico_ou_avisa(capsys, servidor):
    Fake.extras = [dict(os_t(1, 121, 10), id="76580")]
    cod, out, _ = rodar_desat(capsys, servidor, "--tecnicos", "121")
    assert cod == 0 and "Histórico (últimas 3):" in out and "atualização 7" in out and "atualização 4" not in out
    Fake.permitir_historico = False
    cod, out, _ = rodar_desat(capsys, servidor, "--tecnicos", "121")
    assert "Histórico: indisponível" in out and "Mensagem: mensagem da 1 / segunda linha" in out


def test_desatualizadas_silencio_fim_de_semana_e_sem_pendencia(capsys, servidor):
    Fake.extras = [os_t(1, 121, 10)]
    sabado = datetime(2026, 11, 7, 8, 0, 0)
    cod, out, _ = rodar_desat(capsys, servidor, "--tecnicos", "121", "--so-dias-uteis", agora=sabado)
    assert cod == 0 and out == ""
    Fake.extras = [os_t(1, 121, 1)]
    cod, out, _ = rodar_desat(capsys, servidor, "--tecnicos", "121")
    assert cod == 0 and out == ""


def test_desatualizadas_paginacao_e_partes(capsys, servidor):
    Fake.extras = [os_t(1000 + i, 121, 10 + i) for i in range(65)]
    cod, out, err = rodar_desat(capsys, servidor, "--tecnicos", "121")
    assert cod == 0 and err == ""
    blocos = [l for l in out.splitlines() if l.startswith("O.S. ") and " | " in l and not l.startswith("O.S. desatualizadas")]
    assert len(blocos) == 65
    partes = out.split("<<<PARTE>>>")
    assert len(partes) > 1 and all(len(x) <= m.LIMITE_TELEGRAM + 5 for x in partes)
    # mais antiga primeiro: a de 74 dias (id 1064) vem antes da de 10 dias (id 1000)
    assert out.index("O.S. 1064") < out.index("O.S. 1000")


def test_desatualizadas_exige_tecnicos_e_so_leitura(capsys, servidor):
    cod, out, err = rodar_desat(capsys, servidor)
    assert cod == 1 and "informe --tecnicos" in err
    cod, out, err = rodar_desat(capsys, servidor, "--tecnicos", "12a")
    assert cod == 1 and "só números" in err
    assert all(c[0] == "POST" and c[2] == "listar" for c in Fake.chamadas)


def test_skill_os_desatualizadas():
    import yaml
    t = (Path(m.__file__).parent / "skill-os-desatualizadas.md").read_text(encoding="utf-8")
    d = yaml.safe_load(t.split("---")[1])
    assert d["name"] == "os-desatualizadas" and len(d["description"]) <= 1024
    for frase in ("SOMENTE LEITURA", "--desatualizadas --tecnicos 121,161", "<<<PARTE>>>", "NÃO envie mensagem", "NUNCA usar curl"):
        assert frase in t, frase
