---
name: abrir-os-noc
description: Abre no IXC a OS de falha de circuito (assunto Geral) quando o colaborador do NOC colar um chamado (OEMP, e-mail ou Opa) e pedir para abrir a OS, devolve o ID da OS e depois registra "Executar" quando o parceiro for acionado. Use sempre que o colaborador colar os dados de um chamado (designação) e pedir para criar, abrir, gerar ou registrar a OS, em qualquer variação, como "crie essa O.S", "cria a OS", "abre a OS", "abrir OS", "gera a OS", "abre o chamado".
---

# Abertura de OS no NOC (versão 2: o script grava)

**Colaborador padrão desta pessoa: Julio (id 14, Julio Cesar).** Use este id como responsável sem perguntar.

Arquivo de apoio: /opt/data/preparar_os.py (não altere). O script consulta e grava no IXC sozinho. Por padrão ele só SIMULA; só grava com --gravar.

## 0. Pedido de criar OS: a primeira ação é sempre a simulação
Quando o colaborador pedir para criar, abrir, gerar ou registrar uma OS (por exemplo "crie essa OS"), esta skill é o ÚNICO caminho. A primeira coisa que você faz é pegar designação, chamado interno e motivo (passo 3) e rodar a simulação do passo 4. Antes disso é PROIBIDO:
- consultar o IXC por conta própria (buscar contrato, cliente, interconexão, OS parecidas "para ver o padrão");
- usar a api_integracao, outra skill, dashboard, tarefa ou lembrete;
- escolher assunto, contrato, técnico, setor, filial ou prioridade. Quem decide tudo isso é o script: assunto 55 (Geral), setor 14 (NOC), filial 2, prioridade Normal (N), técnico = o colaborador que abre. Nunca use assunto 14 (Reparo), prioridade "1" nem técnico "1".
Se a conversa tiver reiniciado (/new) e você perdeu o contexto, não invente nada e não diga que "perdeu o contexto do que seria registrado": peça de novo os dados do chamado e recomece pelo passo 3.

## 1. Segurança (valem sempre)
1. Só use --gravar depois do OK explícito do colaborador nesta conversa. Sem OK, rode só a simulação. Nunca DELETE.
2. O script pega o acesso sozinho. NUNCA usar curl, nunca ler o cofre-chaves.json nem o token, nunca pedir token.
3. Nunca escrever designação, contrato, cliente ou ID de OS "de memória": só o que o colaborador colou ou o script imprimiu. Nunca corrigir ortografia, acentos ou nomes.
4. Parar no primeiro erro e mostrar a mensagem do script. Se começar com "PARAR", não tente de outro jeito: o colaborador abre a OS pelo caminho manual e você escalona o caso.
5. Se o script disser que o IXC não devolveu o ID, NÃO repita o comando: peça ao colaborador para conferir no IXC se a OS foi aberta.
6. Mostrar só o que o script imprimir. Sem telefone, e-mail ou endereço de cliente.
7. NUNCA reaproveite, resuma nem reescreva uma saída anterior. A cada pedido, rode o script de novo, num único comando que comece com `date;` (exemplo: `date; python3 /opt/data/preparar_os.py ...`), e cole a saída completa, literal, incluindo a linha da data. Se a hora do `data_abertura` não for a de agora, a saída é velha: não use.
8. Nunca grave no IXC por outro caminho (outra ferramenta, outro script, PUT, PATCH ou api_integracao) neste fluxo: só o preparar_os.py, com --gravar e só depois do OK.
9. O acionamento do parceiro é SEMPRE a ação Executar do passo 7. Nunca registre acionamento acrescentando texto na mensagem da OS nem com PUT: isso não muda o status e não conta como executada.
10. Se o script disser que não achou contrato para a designação, não procure por outro caminho (nome do ponto, OEMP, IP, outro contrato parecido) e não use o contrato de uma OS parecida. Peça ao colaborador a designação correta. Designação estranha (por exemplo só um número de cliente, ou sem o prefixo habitual como "SDR ...") também: pergunte antes de rodar.
11. Aprovação: "sim", "pode abrir" ou "aprovado" só vale para a simulação que você acabou de mostrar nesta conversa. Se não houver simulação mostrada, rode-a primeiro.
12. Mostre sempre a saída do script literal. Não escreva "verificação independente" nem resumos seus no lugar da saída: o script já relê a OS e confere os campos.
13. Depois de gravar, informe só o 🔔 ID DA OS e o que o script imprimiu. Se o colaborador disser que vai ajustar algo na tela, não tente corrigir por API.

## 2. Quem está abrindo
O "Colaborador responsável" é quem está abrindo a OS. Se este arquivo trouxer a linha "Colaborador padrão desta pessoa", use-a sem perguntar. Se não trouxer, pergunte o nome uma vez e lembre dele na conversa. Ids no IXC:
Celso 179, Daiana 145, Eliseu 120, Jennypher 184, Maria Eduarda 148, Fernando 71, Marina 101, Rafael 25, Raissa 114, João Vítor 178, Julio 14.
Se o nome não estiver na lista: python3 /opt/data/preparar_os.py --funcionarios "nome", e peça ao colaborador para confirmar o id.

## 3. Receber o chamado
O colaborador cola o texto do chamado (OEMP, e-mail ou Opa). Dele, tire SOMENTE:
- **designação** (ex.: SDR TAF 83108054);
- **chamado interno** (OEMP-xxxxx, ou a referência do e-mail ou do Opa);
- **motivo** exatamente como o cliente abriu (ex.: Inoperante).
O texto vem cru e pode ser bagunçado (assinatura, cabeçalho, várias linhas). Copie a designação exatamente como aparece, sem corrigir. Se houver mais de uma designação no texto, ou nenhuma que pareça uma designação, pergunte qual usar em vez de escolher. Se faltar algum dos três, pergunte só o que falta. Não invente.

## 4. Simular e pedir o OK
date; python3 /opt/data/preparar_os.py --abrir --designacao "<designação>" --chamado "<chamado interno>" --motivo "<motivo>" --colaborador <id>
Mostre a saída EXATAMENTE como veio e pergunte: "Posso abrir esta OS no IXC?". Se vier "PARAR" ou pendências (por exemplo "JÁ EXISTE OS ABERTA"), mostre e pare: não grave. EXCEÇÃO: se o colaborador disser claramente que quer abrir outra OS mesmo com a aberta existente, e citar o número dela, repita o comando acrescentando `--ignorar-os <número>` (só desse número) e mostre a nota que o script imprimir. Nunca use essa opção por conta própria.

## 5. Abrir de verdade (só com OK)
Rode o MESMO comando (com `date;` no começo) e --gravar no fim. Mostre, bem destacado, a linha que o script imprimir:
🔔 ID DA OS: <ID>
→ Coloque este número no campo "Protocolo OEMP" do chamado do cliente (se o chamado veio por e-mail ou Opa, pergunte onde informar).
Se aparecer "⚠️ Conferir no IXC", mostre e peça ao colaborador que confira a OS na tela.
Guarde o ID para o passo 7. Se a conversa for reiniciada (/new) antes do passo 7, peça ao colaborador o número da OS.

## 6. Acionar o parceiro
Pergunte: "Qual é o parceiro desta vez?" (nunca suponha). O acionamento é por WhatsApp, feito pelo colaborador; você não envia nada. Se ele pedir, escreva a mensagem para o parceiro com o motivo e a designação. Depois pergunte: "Já acionou o parceiro?" e espere.

## 7. Registro no IXC (Ações → Executar)
Quando o colaborador confirmar que acionou, rode (a confirmação dele é o OK):
date; python3 /opt/data/preparar_os.py --executar-os <ID> --colaborador <id> --gravar
(a mensagem padrão é "Acionado parceiro via WhatsApp"). Mostre a saída. Se o script recusar ("PARAR") ou não confirmar a execução, não tente de outro jeito: peça ao colaborador para executar na tela do IXC. Encerre perguntando se há outro chamado.

## 8. Modo simulação (teste)
Se o colaborador disser que é teste ou simulação, faça os passos 3 e 4 normalmente (só simulação, nunca --gravar) e depois SIGA a conversa como no fluxo real: pergunte "Qual é o parceiro desta vez?" e, depois da resposta, "Já acionou o parceiro?". Quando ele responder que sim, NÃO rode nada: diga que, no uso real, aqui o script registraria Ações → Executar, e que nada foi gravado no IXC. Não invente ID de OS na simulação.

## 9. Fora desta versão
Registrar andamentos e encerrar OS ainda não estão automatizados.
