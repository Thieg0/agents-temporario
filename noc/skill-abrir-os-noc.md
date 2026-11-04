---
name: abrir-os-noc
description: Prepara a abertura de OS de falha de circuito no IXC (assunto Geral) a partir da designação, e acompanha o acionamento do parceiro. Use quando o NOC colar um chamado de cliente (OEMP, e-mail ou Opa) para abrir OS.
---

# Abertura assistida de OS no NOC (versão 1: prepara, não grava)

Arquivo de apoio: /opt/data/preparar_os.py (instalado uma vez; não altere). O script consulta o IXC sozinho (somente leitura), acha o contrato e monta a descrição. Você conversa com o colaborador e confere o que falta. **Nesta versão quem abre a OS no IXC é o colaborador, na tela.**

## 1. Segurança (valem sempre)
1. SOMENTE LEITURA. Você não cria, altera nem apaga nada no IXC. Nunca DELETE.
2. O script pega o acesso sozinho. NUNCA usar curl, nunca ler o cofre-chaves.json nem o token, nunca pedir token. Se o token aparecer na tela, avisar o supervisor.
3. Nunca escrever designação, contrato, cliente ou ID de OS "de memória": só o que o colaborador colou ou o script imprimiu. Nunca corrigir ortografia, acentos ou nomes.
4. Parar no primeiro erro e mostrar a mensagem do script. Se começar com "PARAR", não tente de outro jeito: diga que o colaborador abre a OS pelo caminho manual e escalone o caso.
5. Mostrar só o que o script imprimir. Sem telefone, e-mail ou endereço de cliente.

## 2. Receber o chamado
O colaborador cola o texto do chamado (OEMP, e-mail ou Opa). Dele, tire SOMENTE:
- **designação** (ex.: SDR TAF 83108054);
- **chamado interno** (o número do chamado do cliente: OEMP-xxxxx, ou a referência do e-mail ou do Opa);
- **motivo** exatamente como o cliente abriu (ex.: Inoperante; se o cliente abriu como inoperante, use Inoperante mesmo que o sintoma seja perda de pacote).
Se faltar algum dos três, pergunte só o que falta. Não invente.

## 3. Rodar o script
python3 /opt/data/preparar_os.py --designacao "<designação>" --chamado "<chamado interno>" --motivo "<motivo>"
Mostre a saída EXATAMENTE como veio. Se aparecer "⚠️ Conferir antes de abrir", destaque os avisos e peça ao colaborador que confirme cada um. Se houver "JÁ EXISTE OS ABERTA", pergunte se é o mesmo problema antes de seguir (risco de OS duplicada).

## 4. O colaborador abre a OS no IXC
Diga: "Confira contrato, cliente e descrição. Abra a OS com assunto 55 (Geral), copiando endereço e filial da OS base, e cole a descrição. Apague as linhas abaixo de Motivo do chamado. Prioridade: confirme com o NOC. Salve e me diga o ID da OS."
Não prossiga até o colaborador informar o ID.

## 5. Depois que ele informar o ID
Mostre, bem destacado:
🔔 ID DA OS: <ID>
→ Coloque este número no campo "Protocolo OEMP" do chamado do cliente.
Se o chamado veio por e-mail ou Opa, pergunte onde esse ID deve ser informado.

## 6. Acionar o parceiro
Pergunte: "Qual é o parceiro desta vez?" (nunca suponha: pode ser a Saturno ou outro). O acionamento é por WhatsApp, feito pelo colaborador; você não envia nada. Se ele pedir, escreva a mensagem para o parceiro com o motivo e a designação (e a VLAN, se ele informar). Depois pergunte: "Já acionou o parceiro?" e espere a resposta.

## 7. Registro no IXC
Quando ele disser que acionou, diga: "No IXC, abra a OS <ID> → Ações → Executar e, no campo Mensagem, escreva: Acionado parceiro via WhatsApp." Encerre perguntando se há outro chamado.

## 8. Fora desta versão
Gravar a OS pelo script, registrar andamentos e encerrar OS ainda não estão automatizados.
