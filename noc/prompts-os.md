# Prompts: abertura de OS do NOC (versão 1, somente leitura)

Anexe no chat do agente: `preparar_os.py` e `skill-abrir-os-noc.md`. Use na ordem, um por vez.
Pré-requisito: o agente já acessa o IXC pelo cofre (o `--testar-acesso` do `os_alerta.py` dá "acesso OK"). O `preparar_os.py` usa o mesmo acesso.

## Prompt 1: instalar (anexe os dois arquivos antes)
Responda sempre em português do Brasil.

Vou te passar dois anexos: preparar_os.py e uma skill. NÃO execute nada além do que está abaixo, não consulte o IXC e não mostre token.
1) Salve o preparar_os.py em /opt/data/preparar_os.py, cópia literal, sem mudar nenhuma linha.
2) Instale o anexo da skill como skill nova (o nome está dentro do arquivo). Se já existir uma skill com o mesmo nome, mova a antiga para a pasta .archive antes, sem apagar.
3) Rode: python3 /opt/data/preparar_os.py --help (isto não consulta o IXC)
4) Responda só com: a versão do Python, se o --help funcionou (sim/não, e o erro se não) e onde a skill ficou.

## Prompt 2: calibrar os campos (somente leitura; roda uma vez)
Responda sempre em português do Brasil.

Rode: python3 /opt/data/preparar_os.py --designacao "SDR TAF 83108054" --descobrir e mostre a saída exatamente como veio. Se der erro, mostre só a mensagem e pare. Não consulte o IXC por outro caminho, não use curl, não mostre token.
(Cole a saída para o Thiego: ela mostra os nomes dos campos da OS e do contrato e confirma se a busca pela designação funciona.)

## Prompt 3: teste real com o chamado do vídeo (somente leitura)
Responda sempre em português do Brasil.

Siga a skill abrir-os-noc. Chamado: designação SDR TAF 83108054, chamado interno OEMP-42074, motivo Inoperante. Rode o script e mostre a saída exatamente como veio. Não grave nada no IXC, não envie nada para ninguém.
Esperado (conferir): contrato 8054, cliente 150, Cliente Final "Video Policia -SEAP-I-078", assunto 55. Se a OS 76196 (aberta no teste do vídeo) aparecer, o script deve avisar "JÁ EXISTE OS ABERTA" e usar a 75811 como base.

## Prompt 4: uso real
O colaborador cola o chamado do cliente no chat e escreve: "Siga a skill abrir-os-noc".

## Prompt 2b: comparar a OS modelo com a OS aberta certa (somente leitura; roda uma vez)
Responda sempre em português do Brasil.

Rode: python3 /opt/data/preparar_os.py --comparar 75811 76196 --mostrar-iguais e mostre a saída exatamente como veio. Se der erro, mostre só a mensagem e pare. Não consulte o IXC por outro caminho, não use curl, não mostre token.
(Cole a saída para o Thiego: ela mostra o que o IXC guardou numa OS aberta corretamente, e é a base para o script gravar a OS.)
