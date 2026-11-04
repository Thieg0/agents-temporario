---
name: aviso-os-tecnico
description: Aviso pessoal de início do dia com as O.S. abertas do técnico e o que merece atenção primeiro. Use no agendamento diário das 8h.
---

# Aviso diário de O.S. do técnico 121

Arquivo de apoio: /opt/data/os_alerta.py (instalado uma vez; não altere). O script consulta o IXC, calcula os fatos e monta a mensagem. Você só roda e escreve a dica de uma frase.

## 1. Segurança (valem sempre)
1. SOMENTE LEITURA. O script só lê o IXC; NUNCA usar POST, PUT ou DELETE nele.
2. O script pega o acesso sozinho (como o script das migrações). NUNCA usar curl, nunca ler o cofre-chaves.json nem o token, e nunca pedir token à pessoa. Se o token aparecer na tela, avisar o supervisor.
3. Não mostrar dados pessoais de clientes. Mostrar só o que o script imprimir.
4. Nunca escrever listas, contagens ou datas "de memória" e nunca recalcular: quem consulta e calcula é o script. Nunca corrigir ortografia, acentos ou nomes.
5. Parar no primeiro erro e mostrar a mensagem do script. Não repetir mais de uma vez e nunca inventar números.

## 2. Rodar o script (ele mesmo consulta o IXC)
python3 /opt/data/os_alerta.py --modo pessoal --tecnico 121 --so-dias-uteis
O script busca todas as páginas de O.S., confere sozinho que são do técnico certo e que a quantidade bate com o "total" do IXC, e monta a mensagem. Não busque nada pela api_integracao e não salve arquivos.
- Se aparecer "Erro: sem acesso ao IXC ...": o token ainda não está disponível para o script. Avise a pessoa com o texto do erro e PARE (quem instala resolve).
- Para testar só o acesso: python3 /opt/data/os_alerta.py --testar-acesso

## 3. Reserva (só se o supervisor mandar)
Se o script não conseguir o acesso mas o supervisor pedir, o modo antigo por arquivos continua existindo: buscar as páginas pela api_integracao, salvar a resposta crua em /opt/data/os_<ID>_AAAA-MM-DD_p<N>.json e rodar com --entrada "<ID>=/opt/data/os_<ID>_AAAA-MM-DD_p*.json". Fora isso, não use.

## 4. Depois de rodar
- Se NÃO imprimir nada (fim de semana ou sem O.S. abertas): NÃO envie mensagem.
- Se imprimir: envie o texto EXATAMENTE como veio e ACRESCENTE no final uma única linha começando com "💡", com a sua sugestão do que fazer primeiro. Use SÓ os fatos do texto (a mais antiga, quantas passam de 30 dias, quantas ainda sem data de assumida, o assunto mais comum). Não invente motivo, cliente ou prazo. Exemplo: "💡 Sugiro começar pela #12345, a mais antiga, e conferir se as 3 sem data de assumida já estão com você."
- Se terminar com erro ("Erro: ..."): avise a pessoa com o texto do erro e PARE.

## 5. Observações
- Não existe prazo/agenda no IXC da Webfoco para essas O.S.; a ordem é por antiguidade. Não diga "para hoje".
- Pausadas (assunto 278) aparecem à parte e não entram no alerta.
- A mensagem não tem dados de cliente: não acrescente nome, endereço ou telefone.
