# Dados para integração: Celso (NOC)

Token Mangaba: sk-sudohhyjyeq2xjoi8j0vr5abyqiitrcnn14l8mpvigfo87tt

Preencha os campos em branco durante a instalação. **Nunca escreva token, senha ou chave de API neste arquivo.**

## Pessoa
- Nome no IXC: Celso Emanuel Berlink Pereira
- Colaborador no IXC (id do "Colaborador responsável"): **179**
- Agente: Assistente NOC de Celso
- Pasta do roteiro: `prompts.md` (nesta pasta)

## IXC
- URL da API: `https://gestorixc.webfoco.net/webservice/v1`
- TOKEN IXC: 149:50bf76cdecc5c54b68dfacb9db0d9e5569bcabef4671a6d73c30fcef699fb6c6

## Telegram
- /sethome feito: [ ] sim

## Skills e arquivos instalados no agente
- [ ] `ixc-work` (mensagem em `mensagem-skill-ixc-work.md`)
- [ ] `/opt/data/preparar_os.py` (sha256 começando com `1cfe2530894815ee`)
- [ ] skill `abrir-os-noc` (arquivo `skill-abrir-os-noc.md` desta pasta; já traz Celso como colaborador padrão)
- [ ] Simulação testada (`--abrir ... --colaborador 179`, sem `--gravar`)
- [ ] Primeiro teste real feito com o Thiego olhando o IXC, em ____/____/______

## Mensagens prontas (copiar e colar no chat do agente, uma por vez)
1. `Vou te passar o acesso ao IXC. Primeiro vou te mandar a URL da API e depois te mando o meu token.`
2. `URL: https://gestorixc.webfoco.net/webservice/v1`
3. `Token: ID:hash` (troque pelo token recebido)
4. `Agente, você possui acesso ao meu e-mail?` e depois `Já fiz a integração, verifique novamente.`
