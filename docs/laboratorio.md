# Referências independentes para revisão de código

Esta seção complementa os estudos dos [projetos reais](../README.md#projetos-reais-em-destaque). Permite inspecionar mecanismos de engenharia sem acesso ao código comercial. O domínio fictício é uma escolha de divulgação; não define a natureza da experiência profissional.

## Cenário

Duas organizações B2B fictícias possuem políticas diferentes de atendimento e devolução. O fluxo responde com fontes ou propõe um follow-up local fictício, sujeito a revisão. O corpus não contém dados de clientes, preços reais ou estratégia comercial dos projetos.

## Componentes

- `contracts.py`: contratos estritos de entrada, aprovação e resposta.
- `retrieval.py`: SQLite FTS5, filtro por tenant e versão do corpus.
- `workflow.py`: LangGraph, checkpoint em memória e aprovação vinculada ao digest.
- `execution.py`: ledger/outbox separado, SQLite em arquivo, transações, reserva exclusiva, recibo correlacionado e reconciliação.
- `execution_probe.py`: experimentos de reinício e recuperação com destino sintético.
- `mcp_server.py` e `mcp_probe.py`: servidor e cliente MCP via stdio.
- `provenance.py`: relações, rejeição de ciclos e análise de impacto.
- `datasets.py`: mensagens sintéticas, validação, deduplicação e split por grupo.
- `evaluate.py`: cenários, critérios de aceite e relatório reproduzível.
- `prompts/support.md`: fronteiras de confiança e contrato de saída demonstrativos.

## Executar e avaliar

Siga os comandos do [README](../README.md#reproduzir-as-referências). O comando de avaliação retorna código diferente de zero quando um cenário falha. A prova MCP inicia um subprocesso local e verifica chamadas reais ao SDK; não conecta a sistemas externos.

## O que observar

1. Tenant alpha não recupera políticas do tenant beta.
2. Uma pergunta sem conhecimento suficiente produz abstenção.
3. Uma citação que não veio da recuperação é rejeitada.
4. Propostas aguardam revisão e rejeitam digest divergente.
5. Repetir a mesma proposta não duplica o efeito fictício.
6. Grupos de exemplos não atravessam a fronteira treino/avaliação.
7. MCP expõe apenas as ferramentas declaradas e valida argumentos.
8. O ledger sobrevive ao reinício e permite somente uma reserva concorrente.
9. Resultado incerto aguarda reconciliação; worker antigo não pode concluir.
10. Falha na auditoria reverte a transição no mesmo domínio transacional.

## Limites

Não há execução de LLM, avaliação de um modelo ajustado, memória conversacional durável, autenticação de usuário ou integração comercial. O ledger possui persistência local; o workflow LangGraph mantém checkpoint em memória. As referências são separadas. Os controles demonstrados não constituem um atestado de segurança ou de prontidão de produção.
