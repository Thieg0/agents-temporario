# Agentes: alerta de prazo das O.S.

Cada pasta tem tudo que aquele agente precisa: `os_alerta.py`, a skill e `prompts.md` (na ordem de uso).

| Pasta | O que recebe |
|---|---|
| `socorro` | relatório diário das 8h com os 3 técnicos (visão de gerente) |
| `milena` (140), `luiz-felipe` (121), `edson` (161), `carlos-henrique` (118), `raissa` (139), `paloma` (144) | aviso pessoal das 8h, só em dias úteis |

## Como funciona (mesmo padrão das migrações)
- O **script consulta o IXC sozinho** (só leitura) e pega o token do mesmo jeito que o `migrar_avantia.py`: `IXC_TOKEN`/`IXC_URL`, ou `IXC_TOKEN_FILE`, ou `dados/.ixc_acesso.json` ao lado do script, ou o **cofre do agente** (`/opt/data/cofre-chaves.json`, entrada "IXC"). O agente nunca vê nem lê o token.
- O agente só **roda o script e envia o texto** (os técnicos ganham uma linha "💡" de dica, escrita pelo agente com os fatos do texto).
- O script confere que as O.S. são do técnico certo e que a quantidade bate com o `total` do IXC, e não imprime dados de cliente.
- `python3 /opt/data/os_alerta.py --testar-acesso` confere o acesso e diz de onde veio ("cofre do agente", "acesso salvo"...).
- Reserva: `--entrada "ID=/opt/data/os_ID_p*.json"` lê respostas já salvas, caso o script não consiga o acesso.

## Regras (confirmadas com o Henrique em 03/11/2026)
Aberta = status diferente de F · Pausada = assunto 278 · Alerta = aberta há mais de 48 h (exceto pausadas) · grupos de 30 dias e 7 dias.

## Testes
`python -m pytest teste -q` (27 testes, com IXC simulado local).
