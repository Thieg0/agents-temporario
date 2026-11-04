---
name: aviso-os-tecnico
description: Aviso pessoal de início do dia com as O.S. abertas do técnico e o que merece atenção primeiro. Use no agendamento diário das 8h.
---

# Aviso diário de O.S. do técnico 140

Arquivo de apoio: /opt/data/os_alerta.py (instalado uma vez; não altere). O script calcula os fatos e monta a mensagem. Você busca os dados, roda, confere e escreve só a dica de uma frase.

## 1. Segurança (valem sempre)
1. SOMENTE LEITURA. NUNCA usar POST, PUT ou DELETE no IXC. Esta skill não altera nada.
2. Usar SOMENTE a ferramenta api_integracao, conforme a descrição dela. NUNCA usar curl nem ler o cofre-chaves.json ou o token. Se o token aparecer na tela, avisar o supervisor.
3. Não mostrar dados pessoais de clientes nem a resposta completa da API. Salvar em arquivo (/opt/data) e mostrar só o que o script imprimir.
4. Nunca escrever listas, contagens ou datas "de memória" e nunca recalcular: quem calcula é o script, sobre os arquivos. Nunca corrigir ortografia, acentos ou nomes.
5. Parar no primeiro erro e mostrar a mensagem do IXC ou do script. Não repetir mais de uma vez e nunca inventar números.
6. Não remover arquivos. Os arquivos de cada dia levam a data no nome, então os de ontem não se misturam com os de hoje.

## 2. Buscar as O.S. de cada técnico (140)
- LEITURA: usar a opção de listagem da ferramenta, com filtro: tabela su_oss_chamado, qtype su_oss_chamado.id_tecnico, oper "=", query <ID do técnico>, rp 30, page 1. Sem escolher campos (volta o registro completo: salvar em arquivo, nunca mostrar).
- Depois page 2, 3, 4... até chegar uma página com MENOS de 30 registros. Não pare antes.
- Salvar a RESPOSTA CRUA de cada página, sem editar nada, em /opt/data/os_<ID>_AAAA-MM-DD_p<N>.json, onde AAAA-MM-DD é a data de hoje (ex.: os_140_2026-11-04_p1.json, os_140_2026-11-04_p2.json). Uma página por arquivo. Não resumir, não filtrar, não conferir "de cabeça".
- Se aparecer "Recurso não está disponível": esperar 5 minutos e tentar uma vez; se persistir, parar e avisar.
- Se o IXC responder erro de permissão ou vazio para um técnico que deveria ter O.S., parar e avisar.

## 3. Rodar o script
python3 /opt/data/os_alerta.py --modo pessoal --tecnico 140 --so-dias-uteis --entrada "/opt/data/os_140_AAAA-MM-DD_p*.json"
(O curinga * pega todas as páginas salvas hoje. O script confere sozinho que as O.S. são do técnico certo e que a quantidade bate com o "total" do IXC; se disser "incompleta", busque as páginas que faltam, salve e rode de novo.)

## 4. Depois de rodar
- Se NÃO imprimir nada (fim de semana ou sem O.S. abertas): NÃO envie mensagem.
- Se imprimir: envie o texto EXATAMENTE como veio e ACRESCENTE no final uma única linha começando com "💡", com a sua sugestão do que fazer primeiro. Use SÓ os fatos do texto (a mais antiga, quantas passam de 30 dias, quantas ainda sem data de assumida, o assunto mais comum). Não invente motivo, cliente ou prazo. Exemplo: "💡 Sugiro começar pela #12345, a mais antiga, e conferir se as 3 sem data de assumida já estão com você."
- Se terminar com erro ("Erro: ..."): avise a pessoa com o texto do erro e PARE.

## 5. Observações
- Não existe prazo/agenda no IXC da Webfoco para essas O.S.; a ordem é por antiguidade. Não diga "para hoje".
- Pausadas (assunto 278) aparecem à parte e não entram no alerta.
- A mensagem não tem dados de cliente: não acrescente nome, endereço ou telefone.
