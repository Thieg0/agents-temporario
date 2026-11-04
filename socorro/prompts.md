# Prompts: socorro

Anexe no chat do agente: os_alerta.py e skill-alerta-prazo-os.md. Use na ordem, um por vez.

## Prompt 1: instalar (anexe os_alerta.py e skill-alerta-prazo-os.md no chat do agente antes)
Responda sempre em português do Brasil.

Vou te passar dois anexos: os_alerta.py e uma skill. NÃO rode com token agora e NUNCA mostre nem peça token.
1) Salve o os_alerta.py em /opt/data/os_alerta.py, cópia literal, sem mudar nenhuma linha.
2) Instale o anexo da skill como skill nova (nome dentro do arquivo). Se já existir uma skill com o mesmo nome ou chamada ixc-leitura/alerta-prazo-os, mova a antiga para a pasta .archive antes, sem apagar.
3) Rode: python3 /opt/data/os_alerta.py --help
4) Responda só com: a versão do Python (python3 --version), se o --help funcionou (sim/não, e o erro se não) e onde a skill ficou.

## Prompt 2: conferir o token (sem mostrar)
Responda sempre em português do Brasil.

Verifique SE a variável de ambiente IXC_TOKEN existe e tem o formato id:hash (um número, dois-pontos e um texto). Responda só "existe e está no formato" ou "não existe" ou "formato errado". NUNCA mostre o valor, nem parte dele, nem o tamanho.

## Prompt 3: teste real (só se o Prompt 2 deu "existe")
Responda sempre em português do Brasil.

Rode: python3 /opt/data/os_alerta.py --modo gerente --tecnicos 140,121,161
Mostre a saída COMPLETA, exatamente como veio, sem editar. Se der erro, mostre só a mensagem "Erro: ..." e pare. Não consulte o IXC por nenhuma outra via.

(Conferir com a tela do IXC. Referência de 03/11 à noite: Milena 10 abertas / 8 em alerta / 2 pausadas; Luiz Felipe 21 abertas; Edson 16 abertas.)

## Prompt 4: agendar (só depois de conferir os números e de ela querer receber)
Responda sempre em português do Brasil.

Substitua o agendamento atual do relatório de O.S. por este: todos os dias úteis às 8h (America/Sao_Paulo), siga a skill alerta-prazo-os. Rode o os_alerta.py no modo gerente com os técnicos 140,121,161, envie a saída exatamente como veio e NÃO envie nada se o script não imprimir nada. Não mostre token. Em caso de erro, me avise com a mensagem do erro. Antes de salvar, me mostre o resumo do agendamento.

## Depois
- Revogar no IXC o token que estava embutido num script de exemplo da skill antiga alerta-prazo-os (e remover o script dela).
- Se o Prompt 2 disser "não existe": o ambiente do agente não passa o token para scripts; falar com quem administra o ambiente (o script precisa ler IXC_TOKEN sem o agente enxergar o valor).
