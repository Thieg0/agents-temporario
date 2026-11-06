# Roteiro de instalação: Fernando (NOC)

Colaborador no IXC: **id 71** (Fernando Rodrigues Oliveira de Souza).
Faça na ordem, um passo por vez, e só passe ao próximo quando o anterior funcionar.
Arquivos de instalação desta pasta: `preparar_os.py` e `skill-abrir-os-noc.md` (a skill já traz o colaborador padrão de Fernando; usados no Passo 4). Os textos do agente (`descricao.txt`, `objetivo.txt`, `personalidade.txt`), os dados do cadastro (`dados-para-integracao.md`) e a skill geral do IXC (`skill-ixc-work.md`) também estão nesta pasta.
Nunca escreva token em arquivo do repositório: ele vai só pelo chat privado do agente, uma vez.

## Passo 0: criar o agente na plataforma Mangaba
1. Criar o agente "Assistente NOC" e colar nos campos Descrição, Objetivo e Personalidade o conteúdo de `descricao.txt`, `objetivo.txt` e `personalidade.txt` (nesta pasta).
2. Cérebro (provedor, modelo e chave): igual aos demais agentes da Webfoco. A chave é enviada na hora e apagada depois.
3. Telegram: criar o bot (BotFather) e informar o id do Telegram de Fernando.
4. Ativar o agente. No Telegram, enviar `/sethome` e depois "apresente-se".

## Passo 1: vincular o e-mail (Google Workspace)
Na plataforma Mangaba:
1. Menu lateral: **Integrações**. No cartão **Google Workspace**, clicar em **Conectar**.
2. Escolher a conta Google de Fernando.
3. Aparece "O Google não verificou este app": é esperado. Clicar em **Avançado** e depois em **Acessar Mangaba Agent (não seguro)**.
4. Marcar **Selecionar tudo** e clicar em **Continuar**.
5. Clicar em **Voltar à Mangaba**. O cartão deve mostrar **Conectado**.

Depois, no chat do Telegram com o agente, uma mensagem por vez:
1. `Agente, você possui acesso ao meu e-mail?` (provavelmente ele diz que não e pede a integração).
2. `Já fiz a integração, verifique novamente.` (agora ele deve dizer que sim).
3. Teste: `Quais foram os e-mails que recebi no dia de hoje?`
Se ele ainda negar: enviar `/new`, repetir a pergunta e, se pedir permissão, escolher **Approve Once**; depois enviar `/sethome`.

## Passo 2: vincular o IXC (URL e token, em duas mensagens)
O token é o do próprio Fernando (gerado no IXC pelo administrador) e é enviado em conversa privada com o agente, uma única vez. Nunca em grupo.
1. `Vou te passar o acesso ao IXC. Primeiro vou te mandar a URL da API e depois te mando o meu token.`
2. `URL: https://gestorixc.webfoco.net/webservice/v1` (o agente deve responder que anotou e que pode enviar o token).
3. `Token: ID:hash` (troque pelo token recebido). A mensagem do token é apagada do chat: é o esperado, não reenvie só por isso.
Se o agente disser que a integração não funcionou, tentar a URL errada ou pedir a URL sem `/webservice`: enviar de novo a URL do item 2. Se disser que o token foi recusado: ele pode ter perdido o token no cofre; enviar o token de novo.

## Passo 3: skill geral do IXC (ixc-work)
Skill completa para todos os colaboradores: consultar clientes, contratos e O.S. (abertas, em execução...), cadastrar cliente, criar contrato e ações de O.S. É um arquivo (grande demais para colar no chat). Anexe o `skill-ixc-work.md` desta pasta no chat do agente e envie:

~~~
Responda sempre em português do Brasil.

Instale o anexo como skill nova (o nome, ixc-work, está dentro do arquivo). Se já existir uma skill ixc-work, mova a antiga para a pasta .archive antes, sem apagar. NÃO execute nada além disso, não consulte o IXC e não mostre token. Responda só com onde a skill ficou e o tamanho do arquivo em bytes.
~~~

Teste (somente leitura): `Use a skill ixc-work e me mostre o contrato 8054 (só id, status e nome do contrato).`
Esperado: dados do contrato 8054 da Oi. Segundo teste: `Use a skill ixc-work e me diga quantas O.S. estão em execução agora (só o total e os 5 primeiros números).` Se disser que não tem permissão, avisar o Thiego (o token pode estar sem a permissão necessária no IXC).

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

Rode: python3 /opt/data/preparar_os.py --funcionarios "Fernando" e mostre a saída exatamente como veio. Se der erro, mostre só a mensagem e pare. Não use curl, não mostre token.
~~~
Esperado: uma linha `id 71 - Fernando Rodrigues Oliveira de Souza`. Se aparecer "sem acesso ao IXC", o cofre dessa máquina não tem o acesso do IXC (volte ao Passo 2). Se aparecer "401", o token foi recusado.

### Prompt 4.3: simulação (não grava nada)
~~~
Responda sempre em português do Brasil.

Rode: python3 /opt/data/preparar_os.py --abrir --designacao "SDR TAF 83108054" --chamado "OEMP-TESTE" --motivo "Inoperante" --colaborador 71 e mostre a saída exatamente como veio. NÃO use --gravar. Se der erro, mostre só a mensagem e pare. Não use curl, não mostre token.
~~~
Esperado: "SIMULAÇÃO: nada foi gravado", colaborador `id 71 - Fernando Rodrigues Oliveira de Souza`, contrato 8054, assunto 55, filial 2, setor 14, prioridade N.
Depois de concluir o Passo 4, envie `/new` e siga para o Passo 5.

## Passo 5: deixar pronto para o uso diário (regras fixas e ensaio)
O fluxo real já foi validado no IXC (OS aberta e executada com sucesso). Aqui não se grava nada: só se confirma que o agente segue a skill. Faça na ordem.

### 5.0: começar uma conversa nova
Depois de instalar ou atualizar qualquer skill ou o script, envie `/new` no chat do agente. Uma conversa aberta antes da instalação pode não enxergar a skill nova (foi o que causou a primeira OS fora do padrão).

### Prompt 5.1: regra fixa
~~~
Responda sempre em português do Brasil.

Regra fixa a partir de agora: quando eu pedir para criar, abrir, gerar ou executar uma O.S. no IXC ("crie essa OS", "abre a OS" ou parecido), você SEMPRE usa a skill abrir-os-noc (script /opt/data/preparar_os.py), com Fernando (id 71) como responsável. A primeira ação é a simulação da skill. Antes dela você NÃO consulta o IXC por conta própria, NÃO usa a api_integracao, NÃO cria dashboard, tarefa nem lembrete e NÃO escolhe assunto, contrato, técnico, setor ou prioridade (quem decide é o script: assunto 55, setor 14, filial 2, prioridade Normal). Só grava depois do meu OK sobre a simulação que você mostrou. O acionamento do parceiro é só a ação Executar da skill, nunca texto acrescentado na mensagem. Se a skill falhar ou o script não achar o contrato, pare e me avise. Confirme em uma linha.
~~~

### Prompt 5.2: ensaio completo, sem gravar
~~~
Responda sempre em português do Brasil.

Isto é uma SIMULAÇÃO, não grave nada. Siga a skill abrir-os-noc. Crie essa O.S: designação SDR TAF 83108054, chamado interno OEMP-TESTE, motivo Inoperante.
~~~
Esperado, nesta ordem: (1) o agente roda `date; python3 /opt/data/preparar_os.py --abrir ... --colaborador 71` sem fazer nenhuma busca antes; (2) mostra "SIMULAÇÃO: nada foi gravado", assunto 55, setor 14, filial 2, prioridade N, contrato 8054; (3) pergunta se pode abrir. Responda `não, é só um teste`. Pronto: o agente seguiu a skill.
Para ensaiar também as perguntas do parceiro, responda `pode abrir, mas é teste, não grave`; ele deve perguntar "Qual é o parceiro desta vez?" e depois "Já acionou o parceiro?", e dizer que nada foi gravado.

### Se o agente sair do padrão
| O que aparece | O que fazer |
|---|---|
| Ele diz "vou verificar a integração", busca OS parecidas ou fala em "padrão das OSs" | Não aprove nada. Envie `/new` e repita o Prompt 5.1 e depois o pedido, começando por `Siga a skill abrir-os-noc.` |
| Assunto 14 (Reparo), prioridade "1", técnico "1", contrato ou interconexão diferentes do script | Não aprove. É sinal de que ele não rodou o script. `/new` e refazer. |
| Ele cria dashboard, tarefa ou "checkpoint" | Escreva `Pare. Não crie nada disso. Siga só a skill abrir-os-noc.` e, se continuar, `/new`. |
| "A sessão foi reiniciada e perdi o contexto" | Normal depois de `/new`: cole de novo os dados do chamado e escreva `Crie essa OS`. |
| O script diz "JÁ EXISTE OS ABERTA" | É a trava de duplicata. Só abra outra se for mesmo necessário, escrevendo `abra outra OS mesmo assim, a aberta é a <número>`. |
| O script diz "PARAR" ou não acha contrato | Confira a designação (copie exatamente do chamado). Não deixe o agente procurar por outro identificador. |
| O agente cola uma saída velha ou sem a data de agora | Escreva `Rode o comando de novo, com date; na frente.` |
| O agente "registrou o acionamento" escrevendo na mensagem da OS | Está errado: o certo é a ação Executar. Escreva `Use o Executar da skill, não edite a mensagem.` |
| Ele não responde ou diz que não tem a skill | Confira com o Prompt 4.1 e `/new`. |

## Depois
- Uso diário: colar os dados do chamado no chat e escrever `Crie essa O.S` (ou variação).
- Se o `--help` falhar por versão do Python (menor que 3.9), avisar o Thiego.
- Toda vez que uma skill ou o script for atualizado, envie `/new` antes de usar.
