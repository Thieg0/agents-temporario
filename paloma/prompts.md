# Prompts: paloma

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

Primeiro rode: python3 /opt/data/os_alerta.py --testar-acesso e me mostre a saída (deve dizer de onde veio o acesso e "acesso OK"). Se der erro, mostre só a mensagem e pare. Depois siga a skill aviso-os-tecnico para o técnico 139, SEM o --so-dias-uteis neste teste: rode o script, mostre a saída COMPLETA, exatamente como veio, e acrescente no final uma linha começando com "💡" com a sua sugestão do que fazer primeiro, usando SÓ os fatos da saída. Não consulte o IXC por outro caminho, não use curl, não mostre token. Se der erro, mostre só a mensagem e pare. Não envie nada para ninguém neste teste.

(Conferir com a tela do IXC. Sem número de referência: compare com a tela do IXC filtrando o técnico 139.)

## Prompt 3: agendar (só depois de conferir os números e de a pessoa querer receber)
Responda sempre em português do Brasil.

Crie um agendamento: seg a sex às 8h (America/Sao_Paulo), siga a skill aviso-os-tecnico para o técnico 139, com --so-dias-uteis. Envie o texto do script exatamente como veio mais a linha "💡" com a dica, e NÃO envie nada se o script não imprimir nada. Não mostre token nem respostas da API. Em caso de erro, me avise com a mensagem do erro. Antes de salvar, me mostre o resumo do agendamento.

## Depois
- Revogar no IXC o token que estava embutido num script de exemplo da skill antiga alerta-prazo-os (e remover o script dela).
- Se aparecer "Erro: sem acesso ao IXC", o script não achou o token (variável, arquivo ou cofre): resolver com quem administra o ambiente antes de seguir. Outro erro ("incompleta", "outro técnico"): rodar de novo uma vez; se repetir, anotar e avisar o Thiego.


---
# Extra: relatório de e-mails da manhã

## Prompt E1: instalar (anexe a skill)
Responda sempre em português do Brasil.

Instale o anexo como skill nova (o nome está dentro do arquivo). NÃO envie nem altere nenhum e-mail. Responda só com onde a skill ficou e se a integração de e-mail está conectada (sim/não).

## Prompt E2: teste (somente leitura)
Responda sempre em português do Brasil.

Rode `date;` e siga a skill relatorio-emails-manha para as últimas 24 horas. Mostre o relatório aqui no chat, sem enviar nada por e-mail. Depois me diga quantas threads leu e quantas ignorou.

(Conferir com a caixa de entrada: só vieram agendamento, boas-vindas e destaques realmente importantes? Algo importante ficou de fora? Se sim, avise o Thieg com o exemplo.)

## Prompt E3: agendar (só depois de conferir)
Responda sempre em português do Brasil.

Crie um agendamento: seg a sex às 8h (America/Sao_Paulo), siga a skill relatorio-emails-manha e envie o relatório aqui no Telegram. NÃO envie nada se não houver e-mails no período. Não envie, responda nem apague e-mails.

## Se o agente sair do padrão
| Sintoma | O que mandar |
|---|---|
| Respondeu ou enviou e-mail | "Pare. Esta rotina é somente leitura. Siga a skill relatorio-emails-manha, seção 1." |
| Mostrou e-mail completo ou telefone | "Siga a regra 4 da skill: sem endereços nem telefones." |
| Listou e-mails demais | "Siga a seção 3 da skill: só agendamento, boas-vindas e no máximo 5 destaques; o resto só entra na contagem de ignorados." |
| Mandou mensagem vazia | "Sem itens nos 3 grupos, não envie nada." |
| Não achou a caixa | Reconectar a integração de e-mail com o supervisor |

## Depois
- Se a cobrança de termo de adesão voltar (com autorização por e-mail), este relatório continua só lendo; as duas rotinas não se misturam.
