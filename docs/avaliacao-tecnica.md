# Roteiros para uma conversa técnica

## Avaliação rápida

- Compare os projetos de [saúde](casos/atendimento-saude.md) e [hotelaria](casos/hospitality.md): problema, desenvolvimento, integrações e continuidade operacional.
- Explore [inteligência multiagente no agronegócio](casos/inteligencia-agronegocio.md), [jornada hospitalar](casos/jornada-hospitalar.md) e [plataformas corporativas](casos/plataformas-corporativas.md) para avaliar desenvolvimento de produto e aplicação em domínios distintos.
- Observe as decisões em [dados e grafos](dados-e-grafos.md) e a expansão de [voz e telefonia](voz-telefonia.md).
- Consulte as [especialidades](competencias.md), as referências de código e a [matriz de evidências](evidencias.md).

## Avaliação de engenharia

Comece pelas fronteiras da solução: fonte de autoridade, estado, identidade, conhecimento, efeitos e recuperação. Discuta seleção entre LangChain/LangGraph, Flowise/Langflow e componentes próprios; o uso de Graphify para impacto; transações e persistência; alternativas de voz e critérios para confirmar transferência humana. Os mecanismos compartilháveis permitem aprofundar essa revisão:

1. Execute os testes e o probe MCP.
2. Analise como fontes e tenant são validados.
3. Inspecione a interrupção do LangGraph e o momento do efeito fictício.
4. Tente retomar com um digest divergente e observe a rejeição.
5. Compare as fronteiras do laboratório com os requisitos de produção.
6. Analise deduplicação e separação de grupos no dataset de fine-tuning.
7. Inspecione a transação do ledger, a aquisição concorrente e o estado de resultado incerto.
8. Examine por que confirmação correlacionada e recibo autenticado são responsabilidades diferentes.
9. Discuta a reconciliação do destino e os limites de uma promessa de execução exatamente uma vez.

## Conversa sobre resultado empresarial

Explore diagnóstico, prioridades, responsabilidade pela continuidade, indicadores e integração com os sistemas existentes. Métricas de clientes e implementação comercial podem ser discutidas somente no contexto autorizado, sem conceder acesso indiscriminado a repositórios.
