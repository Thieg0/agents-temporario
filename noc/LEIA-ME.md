# Agente NOC (modelo de configuração)

Textos prontos para colar nos campos do cadastro do agente na plataforma Mangaba. **Sem chaves de API nem tokens**: elas são enviadas na hora, por mensagem, e apagadas depois.

| Campo | Arquivo | Limite | Tamanho |
|---|---|---|---|
| Descrição | `descricao.txt` | 300 | 270 |
| Objetivo | `objetivo.txt` | 500 | 420 |
| Personalidade | `personalidade.txt` | 3000 | 2986 |

Nome sugerido do agente: **Assistente NOC**. Os três textos dizem que ele também é um assistente que olha e-mail, agenda e Drive de arquivos (só leitura, com a permissão da pessoa). Para isso funcionar, a pessoa precisa conectar a conta Google, como nos demais agentes.

## Como usar
1. Criar o agente (um por pessoa do NOC que ainda não tem) e colar cada arquivo no campo certo.
2. Cérebro (provedor e modelo): igual aos demais agentes da Webfoco. A chave de API é enviada na hora.
3. Telegram: criar o bot e informar o id da pessoa, como nos outros agentes.
4. IXC (só leitura): enviar o token da própria pessoa pelo chat, uma vez, conforme o padrão já usado. Depois testar com uma consulta simples de O.S. de um técnico.
5. Primeiro teste, sem risco: pedir ao agente para triar um incidente fictício ("caiu a PON 3 da OLT do bairro X desde as 14h") e conferir se ele pede o que falta, sugere a severidade e escreve um comunicado em rascunho.

## O que o agente NÃO faz
Não acessa roteadores, OLTs nem sistemas de monitoramento (Zabbix, Grafana etc.) enquanto nenhuma ferramenta for conectada a eles. No IXC só abre e executa O.S. pela skill abrir-os-noc, com o OK da pessoa; nunca apaga. Qualquer ação em equipamento fica com a equipe.

## Próximos passos possíveis (a definir com o setor)
- Ferramenta de leitura do sistema de monitoramento que o NOC usa.
- Aviso diário/de plantão por Telegram com as O.S. abertas por região ou assunto.
- Modelo de comunicado e de post-mortem no padrão da empresa.

## Abertura assistida de OS (versão 2)
Arquivos: `preparar_os.py`, `skill-abrir-os-noc.md`, `prompts-os.md`. O script acha o contrato pela designação, monta a descrição e **abre a OS no IXC** (assunto 55, setor NOC, filial 2, prioridade Normal, endereço do cadastro do cliente), devolvendo "🔔 ID DA OS". Depois executa a OS (Ações → Executar) com "Acionado parceiro via WhatsApp". Por padrão só SIMULA; grava só com `--gravar`, depois do OK do colaborador. O token vem do cofre do agente e o token de cada pessoa precisa permitir criar OS e executar. `--funcionarios "nome"` mostra o id do colaborador. Primeiro teste real: só com o Thiego olhando o IXC (ver `prompts-os.md`). Testes: `python -m pytest teste -q`.

## Uma pasta por pessoa (`pessoas/`)
Cada pessoa do NOC tem a sua pasta em `noc/pessoas/<nome>/` com o roteiro completo (`prompts.md`): criar o agente, vincular o e-mail (Google), vincular o IXC (URL e token em duas mensagens), a skill geral `ixc-work` (consulta, cadastro, alteração e ações de O.S., sem DELETE) e a skill `abrir-os-noc`, com o id do colaborador já preenchido. Também traz cópia do `preparar_os.py` e da skill, para anexar no chat.
As pastas são geradas por `python3 noc/gerar_pastas.py` (a lista de pessoas, os ids e os textos estão nesse arquivo); o teste confere que estão em dia. Ao mudar o `preparar_os.py` ou a skill, rode o gerador de novo e suba tudo junto. Tokens nunca entram no repositório.
