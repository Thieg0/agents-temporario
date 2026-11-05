#!/usr/bin/env python3
"""Gera noc/pessoas/<nome>/ (roteiro da pessoa + cópia do preparar_os.py e da skill) a partir dos modelos desta pasta.

  python3 noc/gerar_pastas.py              escreve as pastas
  python3 noc/gerar_pastas.py --verificar  só confere se as pastas estão em dia (código 1 se não)

Para mudar o texto do roteiro: edite MODELO_ROTEIRO e MENSAGEM_IXC_WORK aqui e rode de novo. Nunca coloque token aqui.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PESSOAS = [  # (pasta, nome completo no IXC, primeiro nome, id do colaborador no IXC)
    ("celso", "Celso Emanuel Berlink Pereira", "Celso", 179),
    ("daiana", "Daiana Valquiria Dias Sousa", "Daiana", 145),
    ("eliseu", "Eliseu dos Santos Pereira Oliveira", "Eliseu", 120),
    ("jennypher", "Jennypher Mychelle Tavares Magalhaes", "Jennypher", 184),
    ("maria-eduarda", "Maria Eduarda Santos da Silva", "Maria Eduarda", 148),
    ("fernando", "Fernando Rodrigues Oliveira de Souza", "Fernando", 71),
    ("marina", "Marina Silva Santos", "Marina", 101),
    ("rafael", "Rafael Cardoso de Azevedo", "Rafael", 25),
    ("raissa", "Raissa Gabriela Ameida Brito", "Raissa", 114),
    ("joao-vitor", "João Vítor Andrade De Carvalho", "João Vítor", 178),
    ("julio", "Julio Cesar", "Julio", 14),
]

MENSAGEM_IXC_WORK = """Responda sempre em português do Brasil.

Crie uma skill chamada ixc-work e salve. Ela serve para trabalhar no IXC da Webfoco: consultar, cadastrar, alterar e fazer ações em O.S.

COMO ACESSAR
- Use SOMENTE a ferramenta api_integracao, conforme a descrição dela. Nunca use curl e nunca leia ou mostre o token.
- URL base: https://gestorixc.webfoco.net/webservice/v1
- CONSULTAR: use a listagem da ferramenta (POST com o cabeçalho ixcsoft: listar), com qtype, query, oper, page e rp.
- Leitura por ID na URL não funciona (erro "Recurso não está disponível"). Filtre assim: qtype <tabela>.id, oper "=", query <id>, page 1, rp 1.
- Para texto parcial use oper "L" (LIKE).
- Peça só os campos necessários, com o prefixo da tabela (exemplo: cliente_contrato.id).
- Não use grid_param (a versão da Webfoco dá erro).
- Busque em páginas de até 30 registros, salve em arquivo e mostre só o resumo.
- Se aparecer "Recurso não está disponível" numa busca com filtro, espere 5 minutos e tente uma vez.

CADASTRAR E ALTERAR
- Cadastrar: POST na tabela. Alterar: PUT em <tabela>/<id>.
- Antes de gravar, mostre um resumo do que vai fazer (tabela, registro e campos) e espere a minha confirmação. Só use confirmado=true depois do meu OK no chat.
- Faça um registro por vez. Depois de gravar, leia o registro de volta e confira se ficou como combinado.
- Datas sempre no formato dd/mm/aaaa.
- O ID de um registro novo só vale se vier na resposta do POST. Nunca presuma o ID. Se a resposta não trouxer o ID, não repita o POST: confira por busca se foi criado e me avise.
- Se o PUT for recusado, leia o registro antes e envie o corpo completo, mudando só os campos combinados.
- Se aparecer "Feche o formulário e tente novamente", alguém está com o registro aberto no IXC. Me avise, espere e tente uma vez.
- Pare no primeiro erro e mostre a mensagem do IXC.

AÇÕES EM O.S. (POST em endpoints próprios; valem as mesmas regras de confirmação)
- Analisar: su_oss_chamado_analisar com id_chamado, id_setor, id_tecnico, status AN, mensagem, data_inicio e data_final.
- Encaminhar (mudar setor): su_oss_chamado_alterar_setor com id_chamado, id_setor, id_tecnico, id_assunto, mensagem e status EN.
- Executar: su_oss_chamado_executar com id_chamado, mensagem e status EX. Ainda em teste: depois de enviar, leia a O.S. e confira se data_hora_execucao foi preenchida.
- Finalizar: su_oss_chamado_fechar com id_chamado, id_tecnico, data_inicio, data_final, mensagem, gera_comissao (S ou N), finaliza_processo S e status F.
- Nas ações, datas no formato dd/mm/aaaa hh:mm:ss. Status da O.S.: A aberta, AN análise, EN encaminhada, AS assumida, AG agendada, EX execução, F finalizada.
- id_tecnico é o id do colaborador no IXC (tabela funcionarios; filtre por nome com oper "L").

TABELAS MAIS USADAS
- cliente: cadastro de clientes
- cliente_contrato: contratos
- su_oss_chamado: O.S. (aberta é qualquer status diferente de F e C)
- funcionarios: colaboradores (id e nome)

REGRAS
- NUNCA use DELETE (excluir), mesmo que eu peça.
- Só grave o que eu pedir e confirmar."""

MODELO_ROTEIRO = """# Roteiro de instalação: {nome} (NOC)

Colaborador no IXC: **id {id}** ({completo}).
Faça na ordem, um passo por vez, e só passe ao próximo quando o anterior funcionar.
Arquivos desta pasta: `preparar_os.py` e `skill-abrir-os-noc.md` (a skill já traz o colaborador padrão de {nome}; usados no Passo 4). Os textos do agente (descrição, objetivo, personalidade) estão em `../../descricao.txt`, `../../objetivo.txt` e `../../personalidade.txt`.
Nunca escreva token em arquivo do repositório: ele vai só pelo chat privado do agente, uma vez.

## Passo 0: criar o agente na plataforma Mangaba
1. Criar o agente "Assistente NOC" e colar nos campos Descrição, Objetivo e Personalidade o conteúdo dos três arquivos acima.
2. Cérebro (provedor, modelo e chave): igual aos demais agentes da Webfoco. A chave é enviada na hora e apagada depois.
3. Telegram: criar o bot (BotFather) e informar o id do Telegram de {nome}.
4. Ativar o agente. No Telegram, enviar `/sethome` e depois "apresente-se".

## Passo 1: vincular o e-mail (Google Workspace)
Na plataforma Mangaba:
1. Menu lateral: **Integrações**. No cartão **Google Workspace**, clicar em **Conectar**.
2. Escolher a conta Google de {nome}.
3. Aparece "O Google não verificou este app": é esperado. Clicar em **Avançado** e depois em **Acessar Mangaba Agent (não seguro)**.
4. Marcar **Selecionar tudo** e clicar em **Continuar**.
5. Clicar em **Voltar à Mangaba**. O cartão deve mostrar **Conectado**.

Depois, no chat do Telegram com o agente, uma mensagem por vez:
1. `Agente, você possui acesso ao meu e-mail?` (provavelmente ele diz que não e pede a integração).
2. `Já fiz a integração, verifique novamente.` (agora ele deve dizer que sim).
3. Teste: `Quais foram os e-mails que recebi no dia de hoje?`
Se ele ainda negar: enviar `/new`, repetir a pergunta e, se pedir permissão, escolher **Approve Once**; depois enviar `/sethome`.

## Passo 2: vincular o IXC (URL e token, em duas mensagens)
O token é o do próprio {nome} (gerado no IXC pelo administrador) e é enviado em conversa privada com o agente, uma única vez. Nunca em grupo.
1. `Vou te passar o acesso ao IXC. Primeiro vou te mandar a URL da API e depois te mando o meu token.`
2. `URL: https://gestorixc.webfoco.net/webservice/v1` (o agente deve responder que anotou e que pode enviar o token).
3. `Token: ID:hash` (troque pelo token recebido). A mensagem do token é apagada do chat: é o esperado, não reenvie só por isso.
Se o agente disser que a integração não funcionou, tentar a URL errada ou pedir a URL sem `/webservice`: enviar de novo a URL do item 2. Se disser que o token foi recusado: ele pode ter perdido o token no cofre; enviar o token de novo.

## Passo 3: skill geral do IXC (ixc-work)
Enviar ao agente a mensagem abaixo, inteira (é um texto só):

~~~
{ixc_work}
~~~

Teste (somente leitura): `Use a skill ixc-work e me mostre o contrato 8054 (só id, status e nome do contrato).`
Esperado: dados do contrato 8054 da Oi. Se disser que não tem permissão, avisar o Thiego (o token pode estar sem a permissão necessária no IXC).

## Passo 4: skill abrir-os-noc (abrir a OS e executar)
Anexe `preparar_os.py` e `skill-abrir-os-noc.md` (os desta pasta, não os da pasta `noc`) no chat do agente. Um prompt por vez.

### Prompt 4.1: instalar
~~~
Responda sempre em português do Brasil.

Vou te passar dois anexos: preparar_os.py e uma skill. NÃO execute nada além do que está abaixo, não consulte o IXC e não mostre token.
1) Salve o preparar_os.py em /opt/data/preparar_os.py, cópia literal, sem mudar nenhuma linha (se já existir, mova a antiga para .archive antes).
2) Instale o anexo da skill como skill nova (o nome está dentro do arquivo). Se já existir uma skill com o mesmo nome, mova a antiga para a pasta .archive antes, sem apagar.
3) Rode: python3 /opt/data/preparar_os.py --help (isto não consulta o IXC)
4) Responda só com: a versão do Python, se o --help funcionou (sim/não, e o erro se não) e onde a skill ficou. O --help deve listar --abrir, --executar-os e --gravar.
~~~

### Prompt 4.2: conferir o acesso e o seu id (somente leitura)
~~~
Responda sempre em português do Brasil.

Rode: python3 /opt/data/preparar_os.py --funcionarios "{nome}" e mostre a saída exatamente como veio. Se der erro, mostre só a mensagem e pare. Não use curl, não mostre token.
~~~
Esperado: uma linha `id {id} - {completo}`. Se aparecer "sem acesso ao IXC", o cofre dessa máquina não tem o acesso do IXC (volte ao Passo 2). Se aparecer "401", o token foi recusado.

### Prompt 4.3: simulação (não grava nada)
~~~
Responda sempre em português do Brasil.

Rode: python3 /opt/data/preparar_os.py --abrir --designacao "SDR TAF 83108054" --chamado "OEMP-TESTE" --motivo "Inoperante" --colaborador {id} e mostre a saída exatamente como veio. NÃO use --gravar. Se der erro, mostre só a mensagem e pare. Não use curl, não mostre token.
~~~
Esperado: "SIMULAÇÃO: nada foi gravado", colaborador `id {id} - {completo}`, contrato 8054, assunto 55, filial 2, setor 14, prioridade N.

## Passo 5: primeiro uso real (com o Thiego olhando o IXC)
O primeiro teste com gravação é só com um chamado de TESTE e com o Thiego conferindo a OS na tela do IXC (o script nunca apaga: a OS de teste é fechada pela tela).
~~~
Responda sempre em português do Brasil.

Siga a skill abrir-os-noc. Quem abre sou eu, {nome} (id {id}). Chamado de TESTE: designação SDR TAF 83108054, chamado interno OEMP-TESTE, motivo Inoperante. Pare na simulação e peça meu OK. Só depois do meu "pode abrir" use --gravar.
~~~
Depois, para testar o Executar, escreva ao agente: `Já acionei o parceiro`. Conferir na tela do IXC que a OS aparece como executada com a mensagem "Acionado parceiro via WhatsApp".

## Depois
- Uso diário: colar o chamado do cliente no chat e escrever `Siga a skill abrir-os-noc`.
- Se o `--help` falhar por versão do Python (menor que 3.9), avisar o Thiego.
"""


def skill_da_pessoa(p: tuple) -> str:
    """A skill é a mesma para todos; só ganha a linha com o colaborador padrão da pessoa, logo depois do título."""
    base = (AQUI / "skill-abrir-os-noc.md").read_text(encoding="utf-8")
    linha = f"\n**Colaborador padrão desta pessoa: {p[2]} (id {p[3]}, {p[1]}).** Use este id como responsável sem perguntar.\n"
    marca = "# Abertura de OS no NOC (versão 2: o script grava)\n"
    assert marca in base
    return base.replace(marca, marca + linha, 1)


def gerar_roteiro(p: tuple) -> str:
    _, completo, nome, cid = p
    return MODELO_ROTEIRO.format(nome=nome, id=cid, completo=completo, ixc_work=MENSAGEM_IXC_WORK)


def esperado() -> dict[Path, bytes]:
    saida: dict[Path, bytes] = {}
    for p in PESSOAS:
        pasta = AQUI / "pessoas" / p[0]
        saida[pasta / "prompts.md"] = gerar_roteiro(p).encode("utf-8")
        saida[pasta / "preparar_os.py"] = (AQUI / "preparar_os.py").read_bytes()
        saida[pasta / "skill-abrir-os-noc.md"] = skill_da_pessoa(p).encode("utf-8")
    return saida


def principal(argv: list[str]) -> int:
    alvo = esperado()
    if "--verificar" in argv:
        fora = [str(c.relative_to(AQUI)) for c, b in alvo.items() if not c.exists() or c.read_bytes() != b]
        if fora:
            print("Pastas desatualizadas (rode: python3 noc/gerar_pastas.py):\n  " + "\n  ".join(fora))
            return 1
        print("Pastas em dia.")
        return 0
    for c, b in alvo.items():
        c.parent.mkdir(parents=True, exist_ok=True)
        c.write_bytes(b)
    print(f"{len(PESSOAS)} pastas geradas em noc/pessoas/")
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
