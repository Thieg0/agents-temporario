# Prompts: paloma

Anexe no chat do agente: os_alerta.py e skill-aviso-os-tecnico.md. Use na ordem, um por vez.

## Prompt 1: instalar (anexe os dois arquivos antes)
Responda sempre em português do Brasil.

Vou te passar dois anexos: os_alerta.py e uma skill. NÃO execute nada além do que está abaixo, não consulte o IXC e não mostre token.
1) Salve o os_alerta.py em /opt/data/os_alerta.py, cópia literal, sem mudar nenhuma linha.
2) Instale o anexo da skill como skill nova (o nome está dentro do arquivo). Se já existir uma skill com o mesmo nome ou chamada ixc-leitura/alerta-prazo-os, mova a antiga para a pasta .archive antes, sem apagar.
3) Rode: python3 /opt/data/os_alerta.py --help
4) Responda só com: a versão do Python (python3 --version), se o --help funcionou (sim/não, e o erro se não) e onde a skill ficou. Se a versão for menor que 3.9, pare e avise.

## Prompt 2: teste real (somente leitura)
Responda sempre em português do Brasil.

Siga a skill aviso-os-tecnico para o técnico 144, SEM o --so-dias-uteis neste teste: busque TODAS as páginas de O.S. dele pela api_integracao, salve a resposta crua de cada página em /opt/data como a skill manda (com a data de hoje no nome), rode o script e mostre a saída COMPLETA, exatamente como veio, e acrescente no final uma linha começando com "💡" com a sua sugestão do que fazer primeiro, usando SÓ os fatos da saída. Não mostre as respostas da API nem token. Se der erro, mostre só a mensagem e pare. Não envie nada para ninguém neste teste.

(Conferir com a tela do IXC. Sem número de referência: compare com a tela do IXC filtrando o técnico 144.)

## Prompt 3: agendar (só depois de conferir os números e de a pessoa querer receber)
Responda sempre em português do Brasil.

Crie um agendamento: seg a sex às 8h (America/Sao_Paulo), siga a skill aviso-os-tecnico para o técnico 144, com --so-dias-uteis. Envie o texto do script exatamente como veio mais a linha "💡" com a dica, e NÃO envie nada se o script não imprimir nada. Não mostre token nem respostas da API. Em caso de erro, me avise com a mensagem do erro. Antes de salvar, me mostre o resumo do agendamento.

## Depois
- Revogar no IXC o token que estava embutido num script de exemplo da skill antiga alerta-prazo-os (e remover o script dela).
- Se o agente errar ao salvar páginas (o script avisa "incompleta" ou "outro técnico"), refazer a busca. Se repetir, anotar e avisar o Thiego.
