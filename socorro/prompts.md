# Prompts: socorro

Anexe no chat do agente: os_alerta.py e skill-alerta-prazo-os.md. Use na ordem, um por vez.

## Prompt 1: instalar (anexe os dois arquivos antes)
Responda sempre em português do Brasil.

Vou te passar dois anexos: os_alerta.py e uma skill. NÃO execute nada além do que está abaixo, não consulte o IXC e não mostre token.
1) Salve o os_alerta.py em /opt/data/os_alerta.py, cópia literal, sem mudar nenhuma linha.
2) Instale o anexo da skill como skill nova (o nome está dentro do arquivo). Se já existir uma skill com o mesmo nome ou chamada ixc-leitura/alerta-prazo-os, mova a antiga para a pasta .archive antes, sem apagar.
3) Rode: python3 /opt/data/os_alerta.py --help (isto não consulta o IXC)
4) Responda só com: a versão do Python (python3 --version), se o --help funcionou (sim/não, e o erro se não) e onde a skill ficou. Se a versão for menor que 3.9, pare e avise.

## Prompt 2: teste real (somente leitura)
Responda sempre em português do Brasil.

Primeiro rode: python3 /opt/data/os_alerta.py --testar-acesso e me mostre a saída (deve dizer de onde veio o acesso e "acesso OK"). Se der erro, mostre só a mensagem e pare. Depois siga a skill alerta-prazo-os para os técnicos 140, 121 e 161: rode o script no modo gerente e mostre a saída COMPLETA, exatamente como veio, sem editar. Não consulte o IXC por outro caminho, não use curl, não mostre token. Não envie nada para ninguém neste teste.

(Conferir com a tela do IXC. Referência de 03/11 à noite: Milena 10 abertas / 8 em alerta / 2 pausadas; Luiz Felipe 21 abertas; Edson 16 abertas. Pode ter mudado; o que importa é bater com a tela.)

## Prompt 3: agendar (só depois de conferir os números e de ela querer receber)
Responda sempre em português do Brasil.

Substitua o agendamento atual do relatório de O.S. por este: todos os dias úteis às 8h (America/Sao_Paulo), siga a skill alerta-prazo-os para os técnicos 140, 121 e 161. Envie a saída do script exatamente como veio e NÃO envie nada se o script não imprimir nada. Não mostre token nem respostas da API. Em caso de erro, me avise com a mensagem do erro. Antes de salvar, me mostre o resumo do agendamento.

## Depois
- Revogar no IXC o token que estava embutido num script de exemplo da skill antiga alerta-prazo-os (e remover o script dela).
- Se aparecer "Erro: sem acesso ao IXC", o script não achou o token (variável, arquivo ou cofre): resolver com quem administra o ambiente antes de seguir. Outro erro ("incompleta", "outro técnico"): rodar de novo uma vez; se repetir, anotar e avisar o Thiego.


---
# Extra: detalhe de O.S. (perguntar mais sobre uma O.S.)

Para quê: a pessoa pergunta "mais informações" ou "últimas atualizações" de uma O.S. (de qualquer forma que escrever) e o agente responde com os dados do IXC. Somente leitura.

Arquivos (nesta pasta): `os_detalhe.py` (script) e `skill-detalhe-os.md` (skill). Instalar neste agente. Antes: `python3 /opt/data/os_alerta.py --testar-acesso` já deve dar "acesso OK" nesse agente (é o mesmo acesso).

## Passo 1: instalar o script
Anexe o `os_detalhe.py` e envie:
~~~
Responda sempre em português do Brasil.

Salve o arquivo anexado em /opt/data/os_detalhe.py (se já existir, mova o antigo para a pasta .archive antes), rode chmod 755 nele e responda só com: date; sha256sum /opt/data/os_detalhe.py; wc -c /opt/data/os_detalhe.py (saída literal). NÃO execute o script e não consulte o IXC.
~~~
Conferir com o hash e o tamanho informados pelo Thiego.

## Passo 2: testar o acesso (somente leitura)
~~~
Responda sempre em português do Brasil.

Rode: date; python3 /opt/data/os_detalhe.py --testar-acesso e me mostre a saída literal. Se der erro, mostre só a mensagem e pare.
~~~
Esperado: `acesso OK (origem do acesso: ...)`.

## Passo 3: instalar a skill
Anexe o `skill-detalhe-os.md` e envie:
~~~
Responda sempre em português do Brasil.

Instale o anexo como skill nova (o nome, detalhe-os, está dentro do arquivo). Se já existir uma skill detalhe-os, mova a antiga para a pasta .archive antes, sem apagar. NÃO execute nada além disso. Responda só com onde a skill ficou e o tamanho do arquivo em bytes.
~~~
Depois envie `/new`.

## Passo 4: testar escrevendo de formas diferentes
Teste pelo menos estas, cada uma numa mensagem separada (sem frase fixa):
1. `me fala mais da O.S. 76580`
2. `o que aconteceu com a 76580?`
3. `últimas atualizações da 76580`
4. `tem alguma OS aberta com a designação SDR TAF 83108054? me mostra detalhes`
5. (Dona Socorro) depois de receber o relatório diário: `me explica melhor a primeira da lista`
Esperado: o agente roda `date; python3 /opt/data/os_detalhe.py ...`, responde em poucas linhas e não inventa nada. Se a saída tiver "Aviso: histórico completo indisponível", é a permissão do token (ver abaixo); o resto deve funcionar.

## Permissão de leitura de Clientes
Para mostrar o nome do cliente e os dados do contrato, o token precisa ler as tabelas `cliente` e `cliente_contrato` (o do NOC não lê `cliente`). Se a saída vier com "Cliente: id N (nome indisponível...)", peça ao administrador do IXC a permissão de LEITURA em Clientes para o token. Sem ela, a skill mostra só os ids.

## Permissão do histórico (pedir ao administrador do IXC)
O histórico completo de atualizações fica na tabela de mensagens da O.S. (`su_oss_chamado_mensagem`). Hoje o token responde "Você não tem permissão para acessar o recurso". Peça ao administrador para liberar a LEITURA (listar/visualizar) das mensagens/histórico de Ordem de Serviço nos tokens da Milena e da Dona Socorro (sem permissão de inserir, editar ou excluir). Sem isso, a skill funciona só com a descrição e a resposta/fechamento da O.S.
Observação: não se sabe ainda se esta é a tabela certa nem os nomes dos campos dela; quando a permissão sair, rodar o Passo 4 e conferir se aparecem as "Últimas atualizações". Se não aparecerem, me avise com a saída para eu ajustar os nomes dos campos.

## Se o agente sair do padrão
| O que aparece | O que fazer |
|---|---|
| Ele usa a api_integracao ou curl em vez do script | `/new` e repetir o pedido começando por `Use a skill detalhe-os.` |
| Cola uma resposta velha, sem a data de agora | `Rode o comando de novo, com date; na frente.` |
| Inventa status ou motivo que não está na saída | `Responda só com o que o script imprimiu.` |
| Pergunta qual O.S. quando a pessoa já citou o número | Normal se o número não estava claro; responda só o número. |
