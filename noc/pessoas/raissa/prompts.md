# Roteiro de instalação: Raissa (NOC)

Colaborador no IXC: **id 114** (Raissa Gabriela Ameida Brito).
Faça na ordem, um passo por vez, e só passe ao próximo quando o anterior funcionar.
Arquivos de instalação desta pasta: `preparar_os.py` e `skill-abrir-os-noc.md` (a skill já traz o colaborador padrão de Raissa; usados no Passo 4). Os textos do agente (`descricao.txt`, `objetivo.txt`, `personalidade.txt`), os dados do cadastro (`dados-para-integracao.md`) e a skill geral do IXC (`skill-ixc-work.md`) também estão nesta pasta.
Nunca escreva token em arquivo do repositório: ele vai só pelo chat privado do agente, uma vez.

## Passo 0: criar o agente na plataforma Mangaba
1. Criar o agente "Assistente NOC" e colar nos campos Descrição, Objetivo e Personalidade o conteúdo de `descricao.txt`, `objetivo.txt` e `personalidade.txt` (nesta pasta).
2. Cérebro (provedor, modelo e chave): igual aos demais agentes da Webfoco. A chave é enviada na hora e apagada depois.
3. Telegram: criar o bot (BotFather) e informar o id do Telegram de Raissa.
4. Ativar o agente. No Telegram, enviar `/sethome` e depois "apresente-se".

## Passo 1: vincular o e-mail (Google Workspace)
Na plataforma Mangaba:
1. Menu lateral: **Integrações**. No cartão **Google Workspace**, clicar em **Conectar**.
2. Escolher a conta Google de Raissa.
3. Aparece "O Google não verificou este app": é esperado. Clicar em **Avançado** e depois em **Acessar Mangaba Agent (não seguro)**.
4. Marcar **Selecionar tudo** e clicar em **Continuar**.
5. Clicar em **Voltar à Mangaba**. O cartão deve mostrar **Conectado**.

Depois, no chat do Telegram com o agente, uma mensagem por vez:
1. `Agente, você possui acesso ao meu e-mail?` (provavelmente ele diz que não e pede a integração).
2. `Já fiz a integração, verifique novamente.` (agora ele deve dizer que sim).
3. Teste: `Quais foram os e-mails que recebi no dia de hoje?`
Se ele ainda negar: enviar `/new`, repetir a pergunta e, se pedir permissão, escolher **Approve Once**; depois enviar `/sethome`.

## Passo 2: vincular o IXC (URL e token, em duas mensagens)
O token é o do próprio Raissa (gerado no IXC pelo administrador) e é enviado em conversa privada com o agente, uma única vez. Nunca em grupo.
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

Rode: python3 /opt/data/preparar_os.py --funcionarios "Raissa" e mostre a saída exatamente como veio. Se der erro, mostre só a mensagem e pare. Não use curl, não mostre token.
~~~
Esperado: uma linha `id 114 - Raissa Gabriela Ameida Brito`. Se aparecer "sem acesso ao IXC", o cofre dessa máquina não tem o acesso do IXC (volte ao Passo 2). Se aparecer "401", o token foi recusado.

### Prompt 4.3: simulação (não grava nada)
~~~
Responda sempre em português do Brasil.

Rode: python3 /opt/data/preparar_os.py --abrir --designacao "SDR TAF 83108054" --chamado "OEMP-TESTE" --motivo "Inoperante" --colaborador 114 e mostre a saída exatamente como veio. NÃO use --gravar. Se der erro, mostre só a mensagem e pare. Não use curl, não mostre token.
~~~
Esperado: "SIMULAÇÃO: nada foi gravado", colaborador `id 114 - Raissa Gabriela Ameida Brito`, contrato 8054, assunto 55, filial 2, setor 14, prioridade N.

## Passo 5: deixar pronto para o uso diário
O fluxo real já foi validado no IXC pelo Thiego (OS aberta e executada com sucesso). Aqui não se grava nada: só se confirma que a skill está ativa e que o agente faz as perguntas na ordem certa.

### Prompt 5.1: ativar
~~~
Responda sempre em português do Brasil.

A skill abrir-os-noc passa a valer para todo pedido meu de criar OS. Quando eu colar os dados de um chamado e escrever "crie essa O.S", "cria a OS", "abre a OS", "gera a OS" ou qualquer variação, siga a skill abrir-os-noc, com Raissa (id 114) como responsável: simule, mostre a saída, peça meu OK, só então grave, mostre o 🔔 ID DA OS, pergunte qual é o parceiro e depois se já acionou. Confirme em uma linha.
~~~

### Prompt 5.2: ensaio completo, sem gravar
~~~
Responda sempre em português do Brasil.

Isto é uma SIMULAÇÃO, não grave nada. Crie essa O.S: designação SDR TAF 83108054, chamado interno OEMP-TESTE, motivo Inoperante.
~~~
Esperado: o agente roda a simulação e mostra a saída, pergunta "Qual é o parceiro desta vez?"; responda `Saturno` e ele pergunta "Já acionou o parceiro?"; responda `sim` e ele deve dizer que nada foi gravado (sem ID de OS). Se o agente tentar gravar ou inventar um ID, escreva ao Thiego.

## Depois
- Uso diário: colar os dados do chamado no chat e escrever `Crie essa O.S` (ou variação).
- Se o `--help` falhar por versão do Python (menor que 3.9), avisar o Thiego.
