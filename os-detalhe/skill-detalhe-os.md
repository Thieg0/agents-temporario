---
name: detalhe-os
description: Responde perguntas sobre uma O.S. específica do IXC e mostra as últimas atualizações dela (descrição, resposta, datas, responsável, status). Use quando a pessoa pedir mais informações, detalhes, andamento, histórico ou atualizações de uma O.S., de qualquer forma que escrever, citando o número, a designação, o cliente, o contrato ou uma linha de relatório.
---

# detalhe-os: detalhes e atualizações de uma O.S. (somente leitura)

Arquivo de apoio: /opt/data/os_detalhe.py (instalado uma vez; não altere). Ele consulta o IXC e imprime os fatos da O.S. Você roda o script e responde à pergunta da pessoa com o que ele imprimiu.

## 1. Segurança (valem sempre)
1. SOMENTE LEITURA. Esta skill nunca grava, altera, executa, finaliza nem exclui nada no IXC. Se a pessoa pedir uma alteração, diga que esta skill só consulta.
2. O script pega o acesso sozinho. NUNCA usar curl, nunca ler o cofre-chaves.json nem o token, nunca pedir token. Se o token aparecer na tela, avise o supervisor.
3. Não use a api_integracao para esta tarefa: use só o script.
4. Responda só com o que o script imprimiu. Nunca invente status, datas, nomes, motivos ou atualizações, e nunca complete com "provavelmente". Se a informação não estiver na saída, diga "não consta".
5. O script mostra o cliente, o contrato e o local da O.S. e nunca imprime telefone, e-mail nem documento. Não busque esses dados por outro caminho e não repasse a saída para fora da conversa.
6. Parar no primeiro erro e mostrar a mensagem do script. Não repetir mais de uma vez.
7. A cada pedido, rode o script de novo (com `date;` na frente). Nunca reaproveite saída de uma consulta anterior.

## 2. A pessoa pode escrever de qualquer jeito
Não existe frase fixa. Descubra o que ela quer pelo sentido e tire os parâmetros da mensagem, do relatório que você acabou de enviar ou da conversa:
- Citou um número de O.S. (ex.: "76580", "OS 76580", "aquela 76580", link do IXC com o id) → `--os 76580`.
- Citou uma linha ou posição do relatório ("a primeira", "a mais antiga", "a do Edson de 12 dias") → pegue o número daquela linha no relatório enviado nesta conversa e use `--os <número>`. Se houver dúvida sobre qual linha, mostre as 2 ou 3 candidatas e pergunte qual.
- Citou uma designação ou texto do chamado (ex.: "SDR BRM 83104884", "OEMP-42798") → `--buscar "<texto>"`.
- Citou um contrato (id) → `--buscar <id> --por contrato`; um cliente (id) → `--buscar <id> --por cliente`.
- Pediu "as últimas atualizações" → acrescente `--ultimas 10` (padrão é 5; máximo 30).
- Sem número nem texto nenhum ("e a O.S. daquele cliente?") → faça UMA pergunta curta pedindo o número ou a designação.
Se a busca devolver várias O.S., mostre a lista curta e pergunte qual a pessoa quer ver. Nunca escolha por conta própria.

## 3. Rodar
date; python3 /opt/data/os_detalhe.py --os <número> [--ultimas N]
date; python3 /opt/data/os_detalhe.py --buscar "<texto>" [--por designacao|contrato|cliente]
- Para testar só o acesso: python3 /opt/data/os_detalhe.py --testar-acesso
- Se aparecer "Erro: sem acesso ao IXC ...": avise a pessoa com o texto do erro e PARE (quem instala resolve).

## 4. O que o script mostra e como responder
- Status, assunto, responsável, prioridade, cliente, contrato (com designação e status do contrato), local da O.S. e datas (abertura, assumida, executada, finalizada). Se a linha do cliente disser "nome indisponível", o acesso não lê a tabela de clientes: informe só o id e avise.
- Descrição (campo mensagem): o texto do chamado; atualizações acrescentadas na tela costumam ficar nele, uma abaixo da outra.
- Resposta / fechamento (campo mensagem_resposta): o que foi escrito ao finalizar ou responder.
- Últimas atualizações: só aparecem se o acesso permitir ler o histórico da O.S. Se a saída trouxer "Aviso: histórico completo indisponível", diga isso à pessoa em uma linha ("só consigo ver a descrição e a resposta da O.S., não o histórico completo") e peça ao supervisor para liberar a leitura do histórico de O.S. no token. Não tente outro caminho.
- Datas com "-" significam que ainda não aconteceu (ex.: sem "Executada em" = não foi executada).

Responda a pergunta que a pessoa fez, com poucas linhas, na ordem: o que ela perguntou, depois o contexto relevante. Se a pessoa pediu "mais informações" sem especificar, resuma: status, responsável, há quanto tempo está aberta, última atualização conhecida e, se houver, o motivo e a resposta. Não copie a saída inteira se ela não pediu: ofereça "quer ver as últimas N atualizações?".
