---
name: relatorio-emails-manha
description: Relatório diário da manhã com os e-mails recebidos e enviados na caixa da pessoa, separados em agendamento, boas-vindas, cobrança e termo de adesão, e restantes. Somente leitura. Use no agendamento diário e quando a pessoa pedir o relatório de e-mails.
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
- Segunda-feira: desde sexta às 18h. Terça a sexta: desde o dia anterior às 18h. Feriado: desde o último dia útil.
- Além disso, liste como "pendentes antigos" apenas as threads de agendamento e termo de adesão dos últimos 7 dias em que o último e-mail é do cliente (ou nosso há mais de 48h úteis sem resposta dele).

## 3. Como classificar (pelo assunto e pelo corpo)
Cada thread entra em UMA categoria, nesta ordem:
1. Agendamento: fala de agendar, reagendar, visita, instalação, data, horário.
2. Boas-vindas: e-mail de boas-vindas de novo cliente ou de ativação.
3. Cobrança e termo de adesão: cobrança de documentos, termo de adesão, assinatura, documentação pendente.
4. Restantes: todo o resto que for de cliente, parceiro ou operação. Ignore propaganda, newsletters, notificações automáticas e spam (conte quantos ignorou, numa linha só).

Na dúvida entre duas categorias, use a primeira da ordem e não explique.

## 4. Formato da mensagem (Telegram, texto simples, sem emojis)
```
Relatório de e-mails - <dia da semana> <dd/mm>
Período: <de> até <agora>

AGENDAMENTO (<n>)
- <cliente/empresa>: <o que pede ou o que falta, 1 linha>. Situação: aguardando nós | aguardando cliente | resolvido.

BOAS-VINDAS (<n>)
- ...

COBRANÇA E TERMO DE ADESÃO (<n>)
- <cliente>: <o que está pendente>. Último contato: <dd/mm>, de <nós|cliente>.

RESTANTES (<n>)
- <remetente/empresa>: <assunto resumido>

Ignorados (propaganda/automáticos): <n>
```
- Categoria sem itens: escreva "nenhum".
- Aguardando nós vem primeiro dentro de cada categoria.
- Máximo 3800 caracteres por mensagem; se passar, divida em partes por categoria.
- Termine com uma única frase dizendo o que merece atenção primeiro.

## 5. O que NÃO fazer
- Não propor nem redigir resposta, a menos que a pessoa peça depois.
- Não abrir anexos nem links.
- Não consultar o IXC.
- Não mudar o formato nem criar categorias novas.
