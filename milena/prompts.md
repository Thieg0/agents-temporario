# Prompts: milena

Anexe no chat do agente: os_alerta.py e skill-aviso-os-tecnico.md. Use na ordem, um por vez.

## Prompt 1: instalar (anexe os dois arquivos antes)
Responda sempre em português do Brasil.

Vou te passar dois anexos: os_alerta.py e uma skill. NÃO execute nada além do que está abaixo, não consulte o IXC e não mostre token.
1) Salve o os_alerta.py em /opt/data/os_alerta.py, cópia literal, sem mudar nenhuma linha.
2) Instale o anexo da skill como skill nova (o nome está dentro do arquivo). Se já existir uma skill com o mesmo nome ou chamada ixc-leitura/alerta-prazo-os, mova a antiga para a pasta .archive antes, sem apagar.
3) Rode: python3 /opt/data/os_alerta.py --help (isto não consulta o IXC)
4) Responda só com: a versão do Python (python3 --version), se o --help funcionou (sim/não, e o erro se não) e onde a skill ficou. Se a versão for menor que 3.9, pare e avise.

## Prompt 2: teste real (somente leitura)
Responda sempre em português do Brasil.

Primeiro rode: python3 /opt/data/os_alerta.py --testar-acesso e me mostre a saída (deve dizer de onde veio o acesso e "acesso OK"). Se der erro, mostre só a mensagem e pare. Depois siga a skill aviso-os-tecnico para o técnico 140, SEM o --so-dias-uteis neste teste: rode o script, mostre a saída COMPLETA, exatamente como veio, e acrescente no final uma linha começando com "💡" com a sua sugestão do que fazer primeiro, usando SÓ os fatos da saída. Não consulte o IXC por outro caminho, não use curl, não mostre token. Se der erro, mostre só a mensagem e pare. Não envie nada para ninguém neste teste.

(Conferir com a tela do IXC. Referência de 03/11 à noite: 10 abertas, 8 em alerta, 2 pausadas.)

## Prompt 3: agendar (só depois de conferir os números e de a pessoa querer receber)
Responda sempre em português do Brasil.

Crie um agendamento: seg a sex às 8h (America/Sao_Paulo), siga a skill aviso-os-tecnico para o técnico 140, com --so-dias-uteis. Envie o texto do script exatamente como veio mais a linha "💡" com a dica, e NÃO envie nada se o script não imprimir nada. Não mostre token nem respostas da API. Em caso de erro, me avise com a mensagem do erro. Antes de salvar, me mostre o resumo do agendamento.

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

## Milena: relatório da manhã das O.S. desatualizadas (Luiz Felipe e Edson)
Somente no agente da Milena, depois dos Passos 1 a 4 (o script é o mesmo). Combinado: todo dia útil de manhã, as O.S. abertas do Luiz Felipe (121) e do Edson (161) sem atualização há mais de 2 dias, com a mensagem da O.S. e o histórico. Ajuste `--dias` se ela quiser outro prazo.

### Passo M1: substituir/instalar a skill (anexe o arquivo novo)
Atenção ao nome: ao anexar de novo, o arquivo pode chegar como `skill-os-desatualizadas(2).md`. O nome do arquivo NÃO importa; o nome da skill é `os-desatualizadas` (campo name dentro do arquivo).
~~~
Responda sempre em português do Brasil.

Substitua a skill os-desatualizadas pelo arquivo anexo (pode ter nome como skill-os-desatualizadas(2).md; ignore o nome do arquivo e use o campo name de dentro dele, que é os-desatualizadas).
1) Localize a skill já instalada com name os-desatualizadas e mova a antiga para a pasta .archive, sem apagar.
2) Instale o anexo com o nome os-desatualizadas (sem "(2)" nem outros sufixos) no lugar dela.
3) Confira que existe UMA só skill os-desatualizadas ativa (nenhuma cópia com "(2)" no nome) e responda só com: onde ela ficou e o tamanho do arquivo em bytes.
NÃO execute o script e não consulte o IXC.
~~~
Depois envie `/new`.

### Passo M2: teste agora (somente leitura)
~~~
Responda sempre em português do Brasil.

Siga a skill os-desatualizadas para os técnicos 121 e 161, com --dias 2, sem --so-dias-uteis. Rode o script com date; na frente e envie o texto exatamente como veio (se vierem partes, uma mensagem por parte). Não grave nada.
~~~
Esperado: um cabeçalho "O.S. desatualizadas (Luiz Felipe, Edson): N sem atualização há mais de 2 dias" e, para cada O.S., UMA LINHA DE TABELA com as colunas O.S. | Responsável | Assunto | Dias parada | Última mensagem (ou o campo mensagem da O.S. se o token não ler a aba Mensagens). Confira com a Milena se as O.S. listadas fazem sentido.

### Passo M3: agendar (só depois de a Milena aprovar o teste)
~~~
Responda sempre em português do Brasil.

Crie um agendamento: seg a sex às 8h10 (America/Sao_Paulo), siga a skill os-desatualizadas para os técnicos 121 e 161, com --dias 2 e --so-dias-uteis. Se o script não imprimir nada, não envie mensagem. Se imprimir, envie o texto exatamente como veio (uma mensagem por parte). Confirme o agendamento com o horário.
~~~

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
