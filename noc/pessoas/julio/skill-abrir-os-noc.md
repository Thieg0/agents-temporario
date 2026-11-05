---
name: abrir-os-noc
description: Abre no IXC a OS de falha de circuito (assunto Geral) a partir do chamado colado pelo NOC, devolve o ID da OS e depois registra "Executar" quando o parceiro for acionado.
---

# Abertura de OS no NOC (versão 2: o script grava)

Arquivo de apoio: /opt/data/preparar_os.py (não altere). O script consulta e grava no IXC sozinho. Por padrão ele só SIMULA; só grava com --gravar.

## 1. Segurança (valem sempre)
1. Só use --gravar depois do OK explícito do colaborador nesta conversa. Sem OK, rode só a simulação. Nunca DELETE.
2. O script pega o acesso sozinho. NUNCA usar curl, nunca ler o cofre-chaves.json nem o token, nunca pedir token.
3. Nunca escrever designação, contrato, cliente ou ID de OS "de memória": só o que o colaborador colou ou o script imprimiu. Nunca corrigir ortografia, acentos ou nomes.
4. Parar no primeiro erro e mostrar a mensagem do script. Se começar com "PARAR", não tente de outro jeito: o colaborador abre a OS pelo caminho manual e você escalona o caso.
5. Se o script disser que o IXC não devolveu o ID, NÃO repita o comando: peça ao colaborador para conferir no IXC se a OS foi aberta.
6. Mostrar só o que o script imprimir. Sem telefone, e-mail ou endereço de cliente.
7. NUNCA reaproveite, resuma nem reescreva uma saída anterior. A cada pedido, rode o script de novo, num único comando que comece com `date;` (exemplo: `date; python3 /opt/data/preparar_os.py ...`), e cole a saída completa, literal, incluindo a linha da data. Se a hora do `data_abertura` não for a de agora, a saída é velha: não use.
8. Nunca grave no IXC por outro caminho (outra ferramenta, outro script, PUT, PATCH ou api_integracao) neste fluxo: só o preparar_os.py, com --gravar e só depois do OK.

## 2. Quem está abrindo
Pergunte o nome de quem está abrindo a OS (será o "Colaborador responsável"). Ids no IXC:
Celso 179, Daiana 145, Eliseu 120, Jennypher 184, Maria Eduarda 148, Fernando 71, Marina 101, Rafael 25, Raissa 114, João Vítor 178, Julio 14.
Se o nome não estiver na lista: python3 /opt/data/preparar_os.py --funcionarios "nome", e peça ao colaborador para confirmar o id.

## 3. Receber o chamado
O colaborador cola o texto do chamado (OEMP, e-mail ou Opa). Dele, tire SOMENTE:
- **designação** (ex.: SDR TAF 83108054);
- **chamado interno** (OEMP-xxxxx, ou a referência do e-mail ou do Opa);
- **motivo** exatamente como o cliente abriu (ex.: Inoperante).
Se faltar algum, pergunte só o que falta. Não invente.

## 4. Simular e pedir o OK
date; python3 /opt/data/preparar_os.py --abrir --designacao "<designação>" --chamado "<chamado interno>" --motivo "<motivo>" --colaborador <id>
Mostre a saída EXATAMENTE como veio e pergunte: "Posso abrir esta OS no IXC?". Se vier "PARAR" ou pendências (por exemplo "JÁ EXISTE OS ABERTA"), mostre e pare: não grave.

## 5. Abrir de verdade (só com OK)
Rode o MESMO comando (com `date;` no começo) e --gravar no fim. Mostre, bem destacado, a linha que o script imprimir:
🔔 ID DA OS: <ID>
→ Coloque este número no campo "Protocolo OEMP" do chamado do cliente (se o chamado veio por e-mail ou Opa, pergunte onde informar).
Se aparecer "⚠️ Conferir no IXC", mostre e peça ao colaborador que confira a OS na tela.
Guarde o ID para o passo 7.

## 6. Acionar o parceiro
Pergunte: "Qual é o parceiro desta vez?" (nunca suponha). O acionamento é por WhatsApp, feito pelo colaborador; você não envia nada. Se ele pedir, escreva a mensagem para o parceiro com o motivo e a designação. Depois pergunte: "Já acionou o parceiro?" e espere.

## 7. Registro no IXC (Ações → Executar)
Quando o colaborador confirmar que acionou, rode (a confirmação dele é o OK):
date; python3 /opt/data/preparar_os.py --executar-os <ID> --colaborador <id> --gravar
(a mensagem padrão é "Acionado parceiro via WhatsApp"). Mostre a saída. Se o script recusar ("PARAR") ou não confirmar a execução, não tente de outro jeito: peça ao colaborador para executar na tela do IXC. Encerre perguntando se há outro chamado.

## 8. Fora desta versão
Registrar andamentos e encerrar OS ainda não estão automatizados.
