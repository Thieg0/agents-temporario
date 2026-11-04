---
name: alerta-prazo-os
description: Relatório de O.S. abertas por técnico com alerta de prazo (visão de gerente). Use para "alerta de prazo das O.S.", relatório diário das 8h.
---

# Alerta de prazo das O.S. (visão de gerente)

SOMENTE LEITURA. Quem calcula é o script; você só roda, confere e envia. NÃO consulte o IXC por outra via, NÃO recalcule, NÃO reescreva a lista.

## Como executar
1. Rode (o token vem da variável de ambiente IXC_TOKEN; nunca mostre nem peça o token):

   python3 /opt/data/os_alerta.py --modo gerente --tecnicos 140,121,161

   (140 Milena, 121 Luiz Felipe, 161 Edson. Para outro técnico, troque a lista de ids.)
2. Se o script não imprimir NADA e terminar sem erro: não há O.S. abertas. NÃO envie mensagem.
3. Se imprimir texto: envie EXATAMENTE como veio (a mensagem já está formatada, com emojis e total). Se o texto trouxer a linha `<<<PARTE>>>`, envie cada parte como uma mensagem separada, sem a linha.
4. Se o script terminar com erro (mensagem "Erro: ..."): avise a pessoa com o texto do erro e PARE. Não tente de novo mais de uma vez e não invente números.

## Regras que o script já aplica (não refaça)
- Aberta = status diferente de F. Pausada = assunto 278 (Pausado/Congelado), em bloco separado, fora do alerta.
- Alerta = aberta há mais de 48 h desde a abertura. Grupos: 🔴 mais de 30 dias, 🟠 7 a 30 dias, 🟡 48 h a 7 dias.
- A mensagem não tem dados de cliente. Não acrescente nome, endereço ou telefone.

## Para perguntas pontuais ("quantas O.S. a Milena tem em alerta?")
Rode com --json e --tecnicos <id> e responda só com os números do JSON.
