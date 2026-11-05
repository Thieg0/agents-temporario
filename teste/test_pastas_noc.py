import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "noc"))
import gerar_pastas as g  # noqa: E402


def test_pastas_em_dia():
    assert g.principal(["--verificar"]) == 0


def test_uma_pasta_por_pessoa_com_nome_e_id_certos():
    assert len(g.PESSOAS) == 11 and len({p[0] for p in g.PESSOAS}) == 11 and len({p[3] for p in g.PESSOAS}) == 11
    for pasta, completo, nome, cid in g.PESSOAS:
        d = RAIZ / "noc" / "pessoas" / pasta
        t = (d / "prompts.md").read_text(encoding="utf-8")
        assert f"id {cid}" in t and completo in t and f'--funcionarios "{nome}"' in t and f"--colaborador {cid} " in t
        assert (d / "preparar_os.py").read_bytes() == (RAIZ / "noc" / "preparar_os.py").read_bytes()
        sk = (d / "skill-abrir-os-noc.md").read_text(encoding="utf-8")
        base = (RAIZ / "noc" / "skill-abrir-os-noc.md").read_text(encoding="utf-8")
        assert f"Colaborador padrão desta pessoa: {nome} (id {cid}," in sk
        assert sk.replace(sk[sk.index("\n**Colaborador padrão"):sk.index("sem perguntar.\n") + len("sem perguntar.\n")], "", 1) == base


def test_ids_conferem_com_os_combinados():
    ids = {p[2]: p[3] for p in g.PESSOAS}
    assert ids == {"Celso": 179, "Daiana": 145, "Eliseu": 120, "Jennypher": 184, "Maria Eduarda": 148, "Fernando": 71,
                   "Marina": 101, "Rafael": 25, "Raissa": 114, "João Vítor": 178, "Julio": 14}


def test_roteiro_tem_todos_os_passos_na_ordem():
    t = (RAIZ / "noc" / "pessoas" / "julio" / "prompts.md").read_text(encoding="utf-8")
    ordem = ["## Passo 0", "## Passo 1: vincular o e-mail", "## Passo 2: vincular o IXC", "## Passo 3: skill geral do IXC", "## Passo 4", "## Passo 5"]
    pos = [t.index(o) for o in ordem]
    assert pos == sorted(pos)
    assert "URL: https://gestorixc.webfoco.net/webservice/v1" in t and "Token: ID:hash" in t


def test_roteiro_nao_deixa_marcador_sem_preencher():
    for p in g.PESSOAS:
        t = g.gerar_roteiro(p)
        assert not re.search(r"\{(nome|id|completo)\}", t)


def test_skill_ixc_work_completa_e_segura():
    s = (RAIZ / "ixc-work" / "skill-ixc-work.md").read_text(encoding="utf-8")
    assert s.startswith("---\nname: ixc-work\n") and "NUNCA use DELETE" in s and "confirmado=true" in s
    for endpoint in ("su_oss_chamado_analisar", "su_oss_chamado_alterar_setor", "su_oss_chamado_executar", "su_oss_chamado_fechar"):
        assert endpoint in s
    for tema in ("Criar cliente", "Criar contrato", "O.S. abertas", "O.S. em execução", "Finalizar", "vd_contratos_produtos", "Abrir uma O.S."):
        assert tema in s, tema
    assert "DELETE " not in s.replace("NUNCA use DELETE", "")
    # a skill geral não depende dos nossos scripts nem de outras skills
    for proibido in ("preparar_os", "abrir-os-noc", ".py", "sha256", "/opt/data", "--gravar", "--comparar"):
        assert proibido not in s, proibido


def test_nenhum_token_no_repositorio():
    padrao = re.compile(r"\b\d{1,4}:[0-9a-f]{24,}\b")
    for f in list((RAIZ / "ixc-work").rglob("*.md")) + list((RAIZ / "noc").rglob("*.md")) + list((RAIZ / "noc").rglob("*.txt")) + list((RAIZ / "noc").rglob("*.py")):
        assert not padrao.search(f.read_text(encoding="utf-8")), f


def test_cada_pasta_tem_textos_do_agente_dados_e_skill_ixc_work():
    for pasta, completo, nome, cid in g.PESSOAS:
        d = RAIZ / "noc" / "pessoas" / pasta
        for f in g.TEXTOS_AGENTE:
            assert (d / f).read_bytes() == (RAIZ / "noc" / f).read_bytes(), (pasta, f)
        assert (d / "dados-para-integracao.md").exists()
        assert (d / "skill-ixc-work.md").read_bytes() == (RAIZ / "ixc-work" / "skill-ixc-work.md").read_bytes()
        assert not (d / "mensagem-skill-ixc-work.md").exists()
        assert "skill-ixc-work.md" in (d / "prompts.md").read_text(encoding="utf-8")


def test_limites_dos_textos_do_agente():
    lim = {"descricao.txt": 300, "objetivo.txt": 500, "personalidade.txt": 3000}
    for f, n in lim.items():
        assert len((RAIZ / "noc" / f).read_text(encoding="utf-8").rstrip("\n")) <= n, f
