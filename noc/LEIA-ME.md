# Agente NOC (modelo de configuração)

Textos prontos para colar nos campos do cadastro do agente na plataforma Mangaba. **Sem chaves de API nem tokens**: elas são enviadas na hora, por mensagem, e apagadas depois.

| Campo | Arquivo | Limite | Tamanho |
|---|---|---|---|
| Descrição | `descricao.txt` | 300 | 273 |
| Objetivo | `objetivo.txt` | 500 | 435 |
| Personalidade | `personalidade.txt` | 3000 | 2990 |

Nome sugerido do agente: **Assistente NOC**.

## Como usar
1. Criar o agente (um por pessoa do NOC que ainda não tem) e colar cada arquivo no campo certo.
2. Cérebro (provedor e modelo): igual aos demais agentes da Webfoco. A chave de API é enviada na hora.
3. Telegram: criar o bot e informar o id da pessoa, como nos outros agentes.
4. IXC (só leitura): enviar o token da própria pessoa pelo chat, uma vez, conforme o padrão já usado. Depois testar com uma consulta simples de O.S. de um técnico.
5. Primeiro teste, sem risco: pedir ao agente para triar um incidente fictício ("caiu a PON 3 da OLT do bairro X desde as 14h") e conferir se ele pede o que falta, sugere a severidade e escreve um comunicado em rascunho.

## O que o agente NÃO faz
Não acessa roteadores, OLTs nem sistemas de monitoramento (Zabbix, Grafana etc.) enquanto nenhuma ferramenta for conectada a eles. Não altera nada no IXC. Qualquer ação em equipamento fica com a equipe.

## Próximos passos possíveis (a definir com o setor)
- Ferramenta de leitura do sistema de monitoramento que o NOC usa.
- Aviso diário/de plantão por Telegram com as O.S. abertas por região ou assunto.
- Modelo de comunicado e de post-mortem no padrão da empresa.
