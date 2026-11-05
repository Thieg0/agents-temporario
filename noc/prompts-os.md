# Prompts: abertura de OS do NOC (versão 2: abre e executa; por padrão só simula)

Anexe no chat do agente: `preparar_os.py` e `skill-abrir-os-noc.md`. Use na ordem, um por vez.
Pré-requisito: o agente já acessa o IXC pelo cofre. O token de cada pessoa precisa ter permissão para criar OS e executar.

## Prompt 1: instalar (anexe os dois arquivos antes)
Responda sempre em português do Brasil.

Vou te passar dois anexos: preparar_os.py e uma skill. NÃO execute nada além do que está abaixo, não consulte o IXC e não mostre token.
1) Salve o preparar_os.py em /opt/data/preparar_os.py, cópia literal, sem mudar nenhuma linha (se já existir, mova a antiga para .archive antes).
2) Instale o anexo da skill como skill nova (o nome está dentro do arquivo). Se já existir uma skill com o mesmo nome, mova a antiga para a pasta .archive antes, sem apagar.
3) Rode: python3 /opt/data/preparar_os.py --help (isto não consulta o IXC)
4) Responda só com: a versão do Python, se o --help funcionou (sim/não, e o erro se não) e onde a skill ficou. O --help deve listar --abrir, --executar-os e --gravar.

## Prompt 2: teste de SIMULAÇÃO (não grava nada)
Responda sempre em português do Brasil.

Rode: python3 /opt/data/preparar_os.py --abrir --designacao "SDR TAF 83108054" --chamado "OEMP-TESTE" --motivo "Inoperante" --colaborador 184 e mostre a saída exatamente como veio. NÃO use --gravar. Se der erro, mostre só a mensagem e pare. Não use curl, não mostre token.
(Esperado: "SIMULAÇÃO", contrato 8054, cliente 150, assunto 55, filial 2, setor 14, prioridade N. Se existir OS aberta com essa designação, o script para e avisa.)

## Prompt 3: primeiro teste REAL (só com o Thiego olhando o IXC; usar um chamado de teste)
Responda sempre em português do Brasil.

Siga a skill abrir-os-noc com este chamado de TESTE: designação SDR TAF 83108054, chamado interno OEMP-TESTE, motivo Inoperante; quem abre: Jennypher (184). Pare na simulação e peça meu OK. Só depois do meu "pode abrir" use --gravar.
(Conferir no IXC: a OS nasce com assunto Geral, cliente Oi Móvel, contrato 8054, setor NOC, endereço do cadastro do cliente, responsável Jennypher. Anotar qualquer campo diferente. O script nunca apaga: a OS de teste é fechada/apagada pela tela do IXC.)

## Prompt 4: teste real do Executar
Depois do Prompt 3, escreva ao agente: "Já acionei o parceiro". Ele roda --executar-os com a mensagem "Acionado parceiro via WhatsApp". Conferir na tela: a OS aparece como executada e a mensagem está no histórico.

## Prompt 5: uso real
O colaborador cola o chamado do cliente no chat e escreve: "Siga a skill abrir-os-noc".

## Extra: achar o id de um colaborador
Rode: python3 /opt/data/preparar_os.py --funcionarios "nome" e mostre a saída exatamente como veio.
