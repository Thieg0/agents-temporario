---
name: os-desatualizadas
description: Relatório da manhã com as O.S. abertas de técnicos que estão sem atualização há alguns dias, com a mensagem e o histórico de cada uma. Use no agendamento diário ou quando a pessoa pedir as O.S. paradas ou desatualizadas de um ou mais técnicos.
---

# os-desatualizadas: O.S. abertas sem atualização (somente leitura)

Arquivo de apoio: /opt/data/os_detalhe.py (o mesmo da skill detalhe-os; instalado uma vez; não altere). Ele consulta o IXC, aplica as regras e imprime o texto pronto. Você só roda e envia.

## 1. Segurança (valem sempre)
1. SOMENTE LEITURA. Nunca grava, altera, executa, finaliza nem exclui nada no IXC.
2. O script pega o acesso sozinho. NUNCA usar curl, nunca ler o cofre-chaves.json nem o token, nunca pedir token. Se o token aparecer na tela, avise o supervisor.
3. Não use a api_integracao para esta tarefa. Nunca escreva listas, datas ou contagens "de memória" e nunca recalcule: quem consulta e calcula é o script.
4. Parar no primeiro erro e mostrar a mensagem do script. Não repetir mais de uma vez e nunca inventar números.
5. Rode o script de novo a cada pedido (com `date;` na frente); nunca reaproveite uma saída antiga.

## 2. Rodar
Técnicos da Milena: Luiz Felipe (121) e Edson (161). Limite padrão: mais de 2 dias sem atualização.
date; python3 /opt/data/os_detalhe.py --desatualizadas --tecnicos 121,161 --dias 2 --so-dias-uteis
- Se a pessoa pedir outros técnicos ou outro prazo ("paradas há mais de 5 dias", "do Edson"), troque `--tecnicos` (ids separados por vírgula) e `--dias`. Ids conhecidos: Milena 140, Luiz Felipe 121, Edson 161, Carlos Henrique 118, Raissa 144, Paloma 139. Se o id não for conhecido, pergunte.
- Para uma consulta fora de agendamento (qualquer dia), tire o `--so-dias-uteis`.

## 3. Depois de rodar
- Se NÃO imprimir nada (fim de semana ou nenhuma O.S. desatualizada): no agendamento, NÃO envie mensagem. Em pedido direto da pessoa, diga "nenhuma O.S. desatualizada".
- Se imprimir: envie EXATAMENTE como veio. Se vier a linha `<<<PARTE>>>`, envie cada parte como uma mensagem separada, na ordem, sem a linha separadora. Não resuma, não reordene, não acrescente dados.
- Se terminar com erro ("Erro: ..."): avise a pessoa com o texto do erro e PARE.
- Se a saída disser "Histórico: indisponível", é a permissão do token; não tente outro caminho.

## 4. Regras do relatório (para você explicar, nunca para recalcular)
- Aberta = status diferente de F (finalizada) e C (cancelada). Pausadas (assunto 278) ficam de fora e são só contadas.
- "Sem atualização" = a data mais recente entre a última atualização da O.S., execução, assunção e abertura. O texto mostra qual campo foi usado.
- Ordem: a mais antiga primeiro, por técnico.
- Cada O.S. traz a mensagem (descrição, com as atualizações escritas nela), a resposta se houver e as últimas atualizações do histórico quando o acesso permitir.
- Se a pessoa pedir detalhes de uma das O.S. do relatório, use a skill detalhe-os com o número daquela O.S.
