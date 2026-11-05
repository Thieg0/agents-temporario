# Dados para integração: Raissa (NOC)

Preencha os campos em branco durante a instalação. **Nunca escreva token, senha ou chave de API neste arquivo.**

## Pessoa
- Nome no IXC: Raissa Gabriela Ameida Brito
- Colaborador no IXC (id do "Colaborador responsável"): **114**
- Agente: Assistente NOC de Raissa
- Pasta do roteiro: `prompts.md` (nesta pasta)

## IXC
- URL da API: `https://gestorixc.webfoco.net/webservice/v1`
- Token: gerado no IXC pelo administrador e enviado só em conversa privada com o agente de Raissa, uma vez, no formato `Token: ID:hash`. A mensagem some do chat (é o esperado).
- Permissões que o token precisa ter: listar contratos, O.S. e funcionários; **criar O.S.** e **executar O.S.**; nada de excluir. Ler Clientes é opcional.
- Token gerado em: ____/____/______   Enviado ao agente em: ____/____/______
- Teste de acesso: `python3 /opt/data/preparar_os.py --funcionarios "Raissa"` deve mostrar `id 114 - Raissa Gabriela Ameida Brito`.

## Google (e-mail, agenda e Drive de arquivos)
- Conta Google de Raissa: ______________________________
- Conectada em Integrações > Google Workspace: [ ] sim, em ____/____/______
- Teste no Telegram: "Quais foram os e-mails que recebi no dia de hoje?": [ ] ok

## Telegram
- Id do Telegram de Raissa: ______________________
- Bot (nome e @): ______________________________
- /sethome feito: [ ] sim

## Plataforma Mangaba
- Id do agente na plataforma: ______________
- Cérebro (provedor e modelo): ______________________ (a chave de API é enviada na hora e apagada depois)
- Descrição, objetivo e personalidade colados (arquivos `descricao.txt`, `objetivo.txt` e `personalidade.txt` desta pasta): [ ] sim

## Skills e arquivos instalados no agente
- [ ] `ixc-work` (mensagem em `mensagem-skill-ixc-work.md`)
- [ ] `/opt/data/preparar_os.py` (sha256 começando com `1cfe2530894815ee`)
- [ ] skill `abrir-os-noc` (arquivo `skill-abrir-os-noc.md` desta pasta; já traz Raissa como colaborador padrão)
- [ ] Simulação testada (`--abrir ... --colaborador 114`, sem `--gravar`)
- [ ] Primeiro teste real feito com o Thiego olhando o IXC, em ____/____/______

## Mensagens prontas (copiar e colar no chat do agente, uma por vez)
1. `Vou te passar o acesso ao IXC. Primeiro vou te mandar a URL da API e depois te mando o meu token.`
2. `URL: https://gestorixc.webfoco.net/webservice/v1`
3. `Token: ID:hash` (troque pelo token recebido)
4. `Agente, você possui acesso ao meu e-mail?` e depois `Já fiz a integração, verifique novamente.`
