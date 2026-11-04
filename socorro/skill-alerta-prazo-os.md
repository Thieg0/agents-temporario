---
name: alerta-prazo-os
description: Relatório de O.S. abertas por técnico com alerta de prazo (visão de gerente). Use para "alerta de prazo das O.S.", relatório diário das 8h.
---

# Alerta de prazo das O.S. (visão de gerente)

Arquivo de apoio: /opt/data/os_alerta.py (instalado uma vez; não altere). O script consulta o IXC, calcula e formata. Você só roda e envia.

## 1. Segurança (valem sempre)
1. SOMENTE LEITURA. O script só lê o IXC; NUNCA usar POST, PUT ou DELETE nele.
2. O script pega o acesso sozinho (como o script das migrações). NUNCA usar curl, nunca ler o cofre-chaves.json nem o token, e nunca pedir token à pessoa. Se o token aparecer na tela, avisar o supervisor.
3. Não mostrar dados pessoais de clientes. Mostrar só o que o script imprimir.
4. Nunca escrever listas, contagens ou datas "de memória" e nunca recalcular: quem consulta e calcula é o script. Nunca corrigir ortografia, acentos ou nomes.
5. Parar no primeiro erro e mostrar a mensagem do script. Não repetir mais de uma vez e nunca inventar números.

## 2. Rodar o script (ele mesmo consulta o IXC)
python3 /opt/data/os_alerta.py --modo gerente --tecnicos 140,121,161
O script busca todas as páginas de O.S. de cada técnico, confere sozinho que são do técnico certo e que a quantidade bate com o "total" do IXC, e monta a mensagem. Não busque nada pela api_integracao e não salve arquivos.
- Se aparecer "Erro: sem acesso ao IXC ...": o token ainda não está disponível para o script. Avise a pessoa com o texto do erro e PARE (quem instala resolve).
- Para testar só o acesso: python3 /opt/data/os_alerta.py --testar-acesso

## 3. Reserva (só se o supervisor mandar)
Se o script não conseguir o acesso mas o supervisor pedir, o modo antigo por arquivos continua existindo: buscar as páginas pela api_integracao, salvar a resposta crua em /opt/data/os_<ID>_AAAA-MM-DD_p<N>.json e rodar com --entrada "<ID>=/opt/data/os_<ID>_AAAA-MM-DD_p*.json" (uma para cada técnico). Fora isso, não use.

## 4. Depois de rodar
- Se o script não imprimir NADA e terminar sem erro: não há O.S. abertas. NÃO envie mensagem.
- Se imprimir texto: envie EXATAMENTE como veio (já formatado, com emojis e total). Se vier a linha `<<<PARTE>>>`, envie cada parte como uma mensagem separada, sem a linha.
- Se terminar com erro ("Erro: ..."): avise a pessoa com o texto do erro e PARE.

## 5. Regras que o script já aplica (não refaça)
Aberta = status diferente de F. Pausada = assunto 278 (Pausado/Congelado), em bloco separado e fora do alerta. Alerta = aberta há mais de 48 h desde a abertura; grupos 🔴 mais de 30 dias, 🟠 7 a 30 dias, 🟡 48 h a 7 dias. A mensagem não tem dados de cliente: não acrescente nome, endereço ou telefone.

## 6. Pergunta pontual ("quantas O.S. a Milena tem em alerta?")
Rode o script no modo gerente com --tecnicos <ID> e --json, e responda só com os números do JSON.
