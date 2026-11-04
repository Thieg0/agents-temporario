---
name: aviso-os-tecnico
description: Aviso pessoal de início do dia com as O.S. abertas do técnico e o que merece atenção primeiro. Use no agendamento diário das 8h.
---

# Aviso diário de O.S. do técnico

SOMENTE LEITURA. O script calcula os fatos; você escreve só a dica de uma frase.

## Como executar (uma vez por dia útil, 8h)
1. Rode, com o id do técnico DONO deste agente (140 Milena, 121 Luiz Felipe, 161 Edson):

   python3 /opt/data/os_alerta.py --modo pessoal --tecnico 140 --so-dias-uteis

   O token vem da variável IXC_TOKEN; nunca mostre nem peça o token.
2. Se NÃO imprimir nada (fim de semana ou sem O.S. abertas): NÃO envie mensagem.
3. Se imprimir: envie o texto EXATAMENTE como veio, e ACRESCENTE no final uma única linha começando com "💡", com a sua sugestão do que fazer primeiro. Use SÓ os fatos que estão no texto (a mais antiga, quantas passam de 30 dias, quantas ainda sem data de assumida, o assunto mais comum). Não invente motivo, cliente ou prazo, e não cite nada que não esteja no texto. Exemplo: "💡 Sugiro começar pela #12345, a mais antiga, e conferir se as 3 sem data de assumida já estão com você."
4. Se o script terminar com erro ("Erro: ..."): avise a pessoa com o texto do erro e PARE.

## Observações
- Não existe prazo/agenda no IXC da Webfoco para essas O.S.; a ordem é por antiguidade. Não diga "para hoje".
- A mensagem não tem dados de cliente. Não acrescente nome, endereço ou telefone.
- Pausadas (assunto 278) aparecem à parte e não entram no alerta.
