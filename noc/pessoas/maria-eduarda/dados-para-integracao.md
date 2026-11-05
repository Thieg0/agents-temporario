# Dados para integração: Maria Eduarda (NOC)

Token Mangaba: sk-sudohhyjyeq2xjoi8j0vr5abyqiitrcnn14l8mpvigfo87tt 

Preencha os campos em branco durante a instalação. **Nunca escreva token, senha ou chave de API neste arquivo.**

## Pessoa
- Nome no IXC: Maria Eduarda Santos da Silva
- Colaborador no IXC (id do "Colaborador responsável"): **148**
- Agente: Assistente NOC de Maria Eduarda
- Pasta do roteiro: `prompts.md` (nesta pasta)

## IXC
- URL da API: `https://gestorixc.webfoco.net/webservice/v1`
- Token: 122:319e5424952ccfa419febb8469ca1d312bc3f88c5c79a6332eead0a6153eb646
- `id 148 - Maria Eduarda Santos da Silva`.

## Google (e-mail, agenda e Drive de arquivos)
- Conta Google de Maria Eduarda: ______________________________
- Conectada em Integrações > Google Workspace: [ ] sim, em ____/____/______
- Teste no Telegram: "Quais foram os e-mails que recebi no dia de hoje?": [ ] ok

## Telegram
- Id do Telegram de Maria Eduarda: ______________________
- Bot (nome e @): ______________________________
- /sethome feito: [ ] sim

## Plataforma Mangaba
- Id do agente na plataforma: ______________
- Cérebro (provedor e modelo): ______________________ (a chave de API é enviada na hora e apagada depois)
- Descrição, objetivo e personalidade colados (arquivos `descricao.txt`, `objetivo.txt` e `personalidade.txt` desta pasta): [ ] sim

## Skills e arquivos instalados no agente
- [ ] skill `ixc-work` (arquivo `skill-ixc-work.md` desta pasta; guia completo do IXC)
- [ ] `/opt/data/preparar_os.py` (sha256 começando com `1cfe2530894815ee`)
- [ ] skill `abrir-os-noc` (arquivo `skill-abrir-os-noc.md` desta pasta; já traz Maria Eduarda como colaborador padrão)
- [ ] Simulação testada (`--abrir ... --colaborador 148`, sem `--gravar`)
- [ ] Primeiro teste real feito com o Thiego olhando o IXC, em ____/____/______

## Mensagens prontas (copiar e colar no chat do agente, uma por vez)
1. `Vou te passar o acesso ao IXC. Primeiro vou te mandar a URL da API e depois te mando o meu token.`
2. `URL: https://gestorixc.webfoco.net/webservice/v1`
3. `Token: ID:hash` (troque pelo token recebido)
4. `Agente, você possui acesso ao meu e-mail?` e depois `Já fiz a integração, verifique novamente.`
