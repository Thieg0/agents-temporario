# Agentes: alerta de prazo das O.S.

Cada pasta tem tudo que aquele agente precisa: os_alerta.py, a skill e prompts.md (na ordem de uso).
- socorro: relatório diário das 8h com os 3 técnicos (visão de gerente)
- milena (140), luiz-felipe (121), edson (161), carlos-henrique (118), raissa (139), paloma (144): aviso pessoal das 8h, dias úteis

Regras: aberta = status diferente de F; pausada = assunto 278; alerta = aberta há mais de 48 h (exceto pausadas).
O script lê o token da variável IXC_TOKEN e só faz leitura. Não há token nem dado de cliente nestes arquivos.
