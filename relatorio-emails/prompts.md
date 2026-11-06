# Prompts: relatório de e-mails da manhã (Raissa e Paloma)

Cada uma faz no próprio agente (a caixa lida é a da pessoa). Anexe skill-relatorio-emails-manha.md. Use na ordem, um por vez.

## Prompt 1: instalar (anexe a skill)
Responda sempre em português do Brasil.

Instale o anexo como skill nova (o nome está dentro do arquivo). NÃO envie nem altere nenhum e-mail. Responda só com onde a skill ficou e se a integração de e-mail está conectada (sim/não).

## Prompt 2: teste (somente leitura)
Responda sempre em português do Brasil.

Rode `date;` e siga a skill relatorio-emails-manha para o período de ontem às 18h até agora. Mostre o relatório aqui no chat, sem enviar nada por e-mail. Depois me diga quantas threads leu e quantas ignorou.

(Conferir com a caixa de entrada: as categorias estão certas? Algo importante ficou em "restantes"? Se sim, avise o Thieg com o exemplo.)

## Prompt 3: agendar (só depois de conferir)
Responda sempre em português do Brasil.

Crie um agendamento: seg a sex às 8h (America/Sao_Paulo), siga a skill relatorio-emails-manha e envie o relatório aqui no Telegram. NÃO envie nada se não houver e-mails no período. Não envie, responda nem apague e-mails.

## Se o agente sair do padrão
| Sintoma | O que mandar |
|---|---|
| Respondeu ou enviou e-mail | "Pare. Esta rotina é somente leitura. Siga a skill relatorio-emails-manha, seção 1." |
| Mostrou e-mail completo ou telefone | "Siga a regra 4 da skill: sem endereços nem telefones." |
| Inventou categoria | "Use só as 4 categorias da seção 3." |
| Mandou mensagem vazia | "Sem e-mails no período, não envie nada." |
| Não achou a caixa | Reconectar a integração de e-mail com o supervisor |

## Depois
- Se a cobrança de termo de adesão voltar (com autorização por e-mail), este relatório continua só lendo; as duas rotinas não se misturam.
