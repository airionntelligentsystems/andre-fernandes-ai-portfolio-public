# Resultados observados no laboratório

Verificação local em 05/10/2026, com Python 3.12.14. Os registros abaixo são resultados de execução do laboratório fictício, sem chamada a um LLM e sem acesso a sistemas comerciais.

| Prova | Resultado observado | Registro |
|---|---|---|
| Testes de contratos, integração e execução durável | Resultado e contagem derivados da execução em JUnit | [Resumo dos testes](verification.json) |
| Harness de aceite | 10 de 10 cenários aprovados | [Resultados por cenário](evaluation.json) |
| MCP cliente/servidor | Catálogo, consulta, proposta e rejeição de tenant inválido verificados via stdio | [Prova MCP](mcp.json) |
| Execução durável | Reinício, reserva expirada, reconciliação e fencing verificados em cinco experimentos | [Experimentos](execution.json) |
| Fine-tuning: preparação dos dados | 12 exemplos sintéticos; 8 para treino e 4 para avaliação; grupos disjuntos | [Relatório e hashes](datasets/report.json) |

A preparação de dados não treina pesos. O baseline de recuperação é lexical. Os testes não estabelecem desempenho de LLMs, segurança de produção ou resultados empresariais. A CI é manual e seu resultado deve ser consultado em cada execução remota.

Para repetir, siga os comandos do [README](../README.md#reproduzir-as-referências). Compare também as versões e os hashes do corpus e do prompt registrados no relatório.
