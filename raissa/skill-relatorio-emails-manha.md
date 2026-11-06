---
name: relatorio-emails-manha
description: Relatório diário da manhã com os e-mails recebidos e enviados na caixa da pessoa, com só três grupos (agendamento, boas-vindas e destaques importantes). Somente leitura. Use no agendamento diário e quando a pessoa pedir o relatório de e-mails.
---

# Relatório de e-mails da manhã

Serve para a pessoa dona deste agente (comercial Webfoco) começar o dia sabendo o que está parado nos e-mails. Você só LÊ e resume.

## 1. Regras que valem sempre
1. SOMENTE LEITURA. Nunca enviar, responder, encaminhar, arquivar, apagar, marcar como lido, criar rascunho nem mudar etiqueta.
2. Ler apenas a caixa da própria pessoa deste agente, pela integração de e-mail já configurada. Nunca pedir senha ou token.
3. Não inventar. Cada item vem de um e-mail que você leu. Se não deu para ler o conteúdo, diga "não consegui ler".
4. Não escrever endereços de e-mail completos nem telefones no relatório; use o nome do cliente ou da empresa. Nada de CPF/CNPJ.
5. Se não houver nenhum e-mail no período, NÃO enviar mensagem.
6. Rode `date;` antes para saber a data real de hoje.

## 2. Período
- Sempre as últimas 24 horas contadas a partir de agora (use o `date;`), inclusive às segundas e depois de feriados.
- Não listar pendências antigas; só o que chegou ou foi enviado nesse período.

## 3. O que entra no relatório (só isto)
Cada thread entra em UMA categoria, nesta ordem:
1. Agendamento: fala de agendar, reagendar, visita, instalação, data, horário.
2. Boas-vindas: e-mail de boas-vindas de novo cliente ou de ativação.
3. Destaques: SOMENTE o que você julgar realmente importante para a pessoa agir ou saber hoje, por exemplo: cliente reclamando ou ameaçando cancelar, pedido urgente ou com prazo, problema de documentação ou termo de adesão travado, resposta que estava aguardando, erro ou recusa de parceiro. Máximo 5 itens; escolha os mais importantes.

TUDO o mais NÃO entra: propaganda, newsletters, notificações automáticas, avisos de sistema, cobranças de rotina, e-mails informativos sem ação, conversas já resolvidas, e-mails internos sem pedido. Esses só são contados numa linha ("Outros e-mails ignorados: N"), sem listar.

Na dúvida se algo é importante, NÃO coloque em destaques.

## 4. Formato da mensagem (Telegram, texto simples, sem emojis)
```
Relatório de e-mails - <dia da semana> <dd/mm>
Período: últimas 24 horas (até <hh:mm>)

AGENDAMENTO (<n>)
- <cliente/empresa>: <o que pede ou o que falta, 1 linha>. Situação: aguardando nós | aguardando cliente | resolvido.

BOAS-VINDAS (<n>)
- <cliente>: <enviado/recebido, 1 linha>

DESTAQUES (<n>)
- <cliente/remetente>: <por que é importante e o que fazer, 1 linha>

Outros e-mails ignorados: <n>
```
- Grupo sem itens: escreva "nenhum".
- Aguardando nós vem primeiro dentro de cada grupo.
- Máximo 3800 caracteres por mensagem.
- Termine com uma única frase dizendo o que merece atenção primeiro.
- Se os três grupos estiverem vazios, NÃO envie mensagem.

## 5. O que NÃO fazer
- Não propor nem redigir resposta, a menos que a pessoa peça depois.
- Não abrir anexos nem links.
- Não consultar o IXC.
- Não mudar o formato nem criar categorias novas.
