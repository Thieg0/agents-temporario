# Agentes: alerta de prazo das O.S.

Cada pasta tem tudo que aquele agente precisa: `os_alerta.py`, a skill e `prompts.md` (na ordem de uso).

| Pasta | O que recebe |
|---|---|
| `socorro` | relatório diário das 8h com os 3 técnicos (visão de gerente) |
| `milena` (140), `luiz-felipe` (121), `edson` (161), `carlos-henrique` (118), `raissa` (139), `paloma` (144) | aviso pessoal das 8h, só em dias úteis |

## Como funciona (mesmo padrão das migrações)
- O agente fala com o IXC **só pela ferramenta `api_integracao`**, de leitura. Nunca `curl`, nunca lê o cofre ou o token.
- Ele salva a **resposta crua** de cada página da listagem em `/opt/data` (com a data de hoje no nome) e roda o script **sobre os arquivos**.
- O `os_alerta.py` não tem token, não tem rede e não escreve nada: lê os arquivos, classifica e monta a mensagem. Confere que as O.S. são do técnico certo e que a quantidade bate com o `total` do IXC.
- A mensagem não tem dados de cliente.

## Regras (confirmadas com o Henrique em 03/11/2026)
Aberta = status diferente de F · Pausada = assunto 278 · Alerta = aberta há mais de 48 h (exceto pausadas) · grupos de 30 dias e 7 dias.

## Testes
`python -m pytest teste -q` (18 testes, sem rede).
