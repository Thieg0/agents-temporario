# Mensagem para criar a skill ixc-work

Envie ao agente, no chat privado, a mensagem abaixo inteira (é um texto só). Ela cria a skill geral do IXC (consultar, cadastrar, alterar e ações em O.S., sem DELETE).

~~~
Responda sempre em português do Brasil.

Crie uma skill chamada ixc-work e salve. Ela serve para trabalhar no IXC da Webfoco: consultar, cadastrar, alterar e fazer ações em O.S.

COMO ACESSAR
- Use SOMENTE a ferramenta api_integracao, conforme a descrição dela. Nunca use curl e nunca leia ou mostre o token.
- URL base: https://gestorixc.webfoco.net/webservice/v1
- CONSULTAR: use a listagem da ferramenta (POST com o cabeçalho ixcsoft: listar), com qtype, query, oper, page e rp.
- Leitura por ID na URL não funciona (erro "Recurso não está disponível"). Filtre assim: qtype <tabela>.id, oper "=", query <id>, page 1, rp 1.
- Para texto parcial use oper "L" (LIKE).
- Peça só os campos necessários, com o prefixo da tabela (exemplo: cliente_contrato.id).
- Não use grid_param (a versão da Webfoco dá erro).
- Busque em páginas de até 30 registros, salve em arquivo e mostre só o resumo.
- Se aparecer "Recurso não está disponível" numa busca com filtro, espere 5 minutos e tente uma vez.

CADASTRAR E ALTERAR
- Cadastrar: POST na tabela. Alterar: PUT em <tabela>/<id>.
- Antes de gravar, mostre um resumo do que vai fazer (tabela, registro e campos) e espere a minha confirmação. Só use confirmado=true depois do meu OK no chat.
- Faça um registro por vez. Depois de gravar, leia o registro de volta e confira se ficou como combinado.
- Datas sempre no formato dd/mm/aaaa.
- O ID de um registro novo só vale se vier na resposta do POST. Nunca presuma o ID. Se a resposta não trouxer o ID, não repita o POST: confira por busca se foi criado e me avise.
- Se o PUT for recusado, leia o registro antes e envie o corpo completo, mudando só os campos combinados.
- Se aparecer "Feche o formulário e tente novamente", alguém está com o registro aberto no IXC. Me avise, espere e tente uma vez.
- Pare no primeiro erro e mostre a mensagem do IXC.

AÇÕES EM O.S. (POST em endpoints próprios; valem as mesmas regras de confirmação)
- Analisar: su_oss_chamado_analisar com id_chamado, id_setor, id_tecnico, status AN, mensagem, data_inicio e data_final.
- Encaminhar (mudar setor): su_oss_chamado_alterar_setor com id_chamado, id_setor, id_tecnico, id_assunto, mensagem e status EN.
- Executar: su_oss_chamado_executar com id_chamado, mensagem e status EX. Ainda em teste: depois de enviar, leia a O.S. e confira se data_hora_execucao foi preenchida.
- Finalizar: su_oss_chamado_fechar com id_chamado, id_tecnico, data_inicio, data_final, mensagem, gera_comissao (S ou N), finaliza_processo S e status F.
- Nas ações, datas no formato dd/mm/aaaa hh:mm:ss. Status da O.S.: A aberta, AN análise, EN encaminhada, AS assumida, AG agendada, EX execução, F finalizada.
- id_tecnico é o id do colaborador no IXC (tabela funcionarios; filtre por nome com oper "L").

TABELAS MAIS USADAS
- cliente: cadastro de clientes
- cliente_contrato: contratos
- su_oss_chamado: O.S. (aberta é qualquer status diferente de F e C)
- funcionarios: colaboradores (id e nome)

REGRAS
- NUNCA use DELETE (excluir), mesmo que eu peça.
- Só grave o que eu pedir e confirmar.
~~~
