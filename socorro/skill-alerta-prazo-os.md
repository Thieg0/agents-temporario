---
name: alerta-prazo-os
description: Relatório de O.S. abertas por técnico com alerta de prazo (visão de gerente). Use para "alerta de prazo das O.S.", relatório diário das 8h.
---

# Alerta de prazo das O.S. (visão de gerente)

Arquivo de apoio: /opt/data/os_alerta.py (instalado uma vez; não altere). Quem calcula e formata é o script. Você busca os dados, roda, confere e envia.

## 1. Segurança (valem sempre)
1. SOMENTE LEITURA. NUNCA usar POST, PUT ou DELETE no IXC. Esta skill não altera nada.
2. Usar SOMENTE a ferramenta api_integracao, conforme a descrição dela. NUNCA usar curl nem ler o cofre-chaves.json ou o token. Se o token aparecer na tela, avisar o supervisor.
3. Não mostrar dados pessoais de clientes nem a resposta completa da API. Salvar em arquivo (/opt/data) e mostrar só o que o script imprimir.
4. Nunca escrever listas, contagens ou datas "de memória" e nunca recalcular: quem calcula é o script, sobre os arquivos. Nunca corrigir ortografia, acentos ou nomes.
5. Parar no primeiro erro e mostrar a mensagem do IXC ou do script. Não repetir mais de uma vez e nunca inventar números.
6. Não remover arquivos. Os arquivos de cada dia levam a data no nome, então os de ontem não se misturam com os de hoje.

## 2. Buscar as O.S. de cada técnico (140, 121, 161)
- LEITURA: usar a opção de listagem da ferramenta, com filtro: tabela su_oss_chamado, qtype su_oss_chamado.id_tecnico, oper "=", query <ID do técnico>, rp 30, page 1. Sem escolher campos (volta o registro completo: salvar em arquivo, nunca mostrar).
- Depois page 2, 3, 4... até chegar uma página com MENOS de 30 registros. Não pare antes.
- Salvar a RESPOSTA CRUA de cada página, sem editar nada, em /opt/data/os_<ID>_AAAA-MM-DD_p<N>.json, onde AAAA-MM-DD é a data de hoje (ex.: os_140_2026-11-04_p1.json, os_140_2026-11-04_p2.json). Uma página por arquivo. Não resumir, não filtrar, não conferir "de cabeça".
- Se aparecer "Recurso não está disponível": esperar 5 minutos e tentar uma vez; se persistir, parar e avisar.
- Se o IXC responder erro de permissão ou vazio para um técnico que deveria ter O.S., parar e avisar.

## 3. Rodar o script
python3 /opt/data/os_alerta.py --modo gerente --tecnicos 140,121,161 --entrada "140=/opt/data/os_140_AAAA-MM-DD_p*.json" --entrada "121=/opt/data/os_121_AAAA-MM-DD_p*.json" --entrada "161=/opt/data/os_161_AAAA-MM-DD_p*.json"
(O curinga * pega todas as páginas salvas hoje. O script confere sozinho que as O.S. são do técnico certo e que a quantidade bate com o "total" do IXC; se disser "incompleta", busque as páginas que faltam, salve e rode de novo.)

## 4. Depois de rodar
- Se o script não imprimir NADA e terminar sem erro: não há O.S. abertas. NÃO envie mensagem.
- Se imprimir texto: envie EXATAMENTE como veio (já formatado, com emojis e total). Se vier a linha `<<<PARTE>>>`, envie cada parte como uma mensagem separada, sem a linha.
- Se terminar com erro ("Erro: ..."): avise a pessoa com o texto do erro e PARE.

## 5. Regras que o script já aplica (não refaça)
Aberta = status diferente de F. Pausada = assunto 278 (Pausado/Congelado), em bloco separado e fora do alerta. Alerta = aberta há mais de 48 h desde a abertura; grupos 🔴 mais de 30 dias, 🟠 7 a 30 dias, 🟡 48 h a 7 dias. A mensagem não tem dados de cliente: não acrescente nome, endereço ou telefone.

## 6. Pergunta pontual ("quantas O.S. a Milena tem em alerta?")
Busque as O.S. do técnico (seção 2), rode o script no modo gerente com --tecnicos <ID> e --json, e responda só com os números do JSON.
