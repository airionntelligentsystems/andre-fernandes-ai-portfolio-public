# Profundidade técnica: decisões, implementação e avaliação

As especialidades formam um repertório integrado de engenharia: modelos e agentes, orquestração, conhecimento, ferramentas, dados, grafos, voz e avaliação. Cada seção expõe o problema, as decisões que considero e a evidência pertinente. As tecnologias compõem meu repertório; o estágio de aplicação é identificado nos estudos de caso.

## LLMs e AI Agents

**Problema:** transformar linguagem e contexto em uma resposta ou proposta útil, preservando a autoridade dos sistemas e os limites de ação.

**Decisões:** decompor intenção, planejamento, chamada de ferramenta e efeito; usar saída estruturada com validação externa; definir orçamento de tokens, deadline e limite de iterações; escolher modelo por tarefa, latência e qualidade observada. Uma falha de esquema pode justificar reparo limitado; falha de autorização encerra a ação. Delegação entre agentes precisa de contratos de entrada, saída e responsabilidade.

**Avaliação:** validade de ferramenta, sustentação factual, conclusão por tipo de tarefa, execução proibida e comportamento diante de indisponibilidade. Uma avaliação real precisa chamar o modelo e registrar suas condições; testes determinísticos verificam outra camada.

**Referência:** [contratos de resposta](../src/portfolio_lab/contracts.py), [arquitetura](arquitetura.md) e [gates de modelo](operacao.md). O laboratório usa síntese extrativa; não executa inferência.

## RAG e memória governada

**Problema:** entregar informação relevante, admissível e atual, sem confundir conhecimento com autoridade transacional.

**Decisões:** registrar origem, versão, revisão, vigência e escopo; definir chunking por unidade de informação e estrutura do documento; recuperar dentro das permissões; combinar candidatos lexicais/vetoriais quando justificado; aplicar reranking com orçamento de latência; manter evidência de citação. Memória precisa de origem, finalidade, expiração e revogação. Dados voláteis devem ser lidos em sua fonte operacional.

**Avaliação:** Recall@k em conjunto rotulado, relevância por consulta, precisão de citação, cobertura das alegações, abstenção correta e latência por etapa. Mudança de chunking ou índice é avaliada com o mesmo corpus de teste; cross-tenant é cenário bloqueador.

**Referência:** [baseline lexical com versão e escopo](../src/portfolio_lab/retrieval.py) e [fronteiras do caso principal](casos/atendimento-saude.md). Busca híbrida e reranking são desenho técnico, sem benchmark semântico publicado.

## MCP

**Problema:** disponibilizar capacidades para aplicações de IA com contratos compreensíveis e controláveis.

**Decisões:** definir esquemas de entrada/saída, erros e efeitos de cada ferramenta; separar leitura, proposta e execução; escolher transporte e mecanismo de autorização apropriados ao ambiente; derivar escopo do principal confiável. O servidor precisa validar chamadas independentemente do modelo. Descrição de ferramenta e anotações não constituem barreira de segurança.

**Avaliação:** negociação cliente/servidor, descoberta, chamada válida, rejeição de argumento, retorno estruturado, escopo e caminho de indisponibilidade. Para transporte remoto, entram verificações específicas de autenticação e audiência.

**Referência:** [servidor tipado](../src/portfolio_lab/mcp_server.py) e [cliente real por stdio](../src/portfolio_lab/mcp_probe.py). A prova local não certifica um gateway remoto.

## LangChain e LangGraph

**Problema:** conectar modelos, ferramentas e conhecimento empresarial e coordenar uma jornada com estado, revisão, retomada e caminhos de erro.

**Decisões:** usar LangChain para composição de modelos, agentes e ferramentas; usar LangGraph quando transições, persistência e controle do fluxo exigem desenho explícito. Modelar estado mínimo, transições e reducers; distinguir estado conversacional do ledger de execução; identificar thread de forma autorizada; selecionar checkpointer e política de retenção; tratar reexecução do nó ao retomar um interrupt. Aprovação fica vinculada à proposta e ao contexto; efeitos não podem ser repetidos por replay inadvertido.

**Avaliação:** recusa, aprovação, payload inválido, mudança de contexto, retomada e recuperação após falha. Persistência de checkpoint e confirmação de operação externa são contratos diferentes.

**Referência:** [grafo com revisão tipada](../src/portfolio_lab/workflow.py), [regressões](../tests/test_workflow.py) e [execução durável separada](confiabilidade.md). O grafo local usa checkpoint em memória; o ledger usa SQLite persistente.

## Engenharia de grafos e Graphify

**Problema:** representar relações que melhoram execução, compreensão de dependências ou recuperação de conhecimento.

**Decisões:** escolher a semântica do grafo antes da ferramenta. Grafo de execução representa estados e transições; grafo de dependências apoia impacto e proveniência; grafo de conhecimento representa entidades e relações com origem e validade. Uso Graphify na estruturação do mapa técnico do projeto de saúde, para navegação, dependências, proveniência e análise de impacto. Restrições de ciclos dependem do domínio: um DAG de dependências pode proibi-los, enquanto uma máquina de estados pode precisar deles.

**Avaliação:** origem das arestas, cobertura do mapa, impacto de alteração e consistência com os artefatos de origem. GraphRAG exige avaliação de recuperação e respostas, além da validade estrutural.

**Referência:** [dados, grafos e fontes de autoridade](dados-e-grafos.md) e [proveniência e impacto](../src/portfolio_lab/provenance.py). Graphify apoia compreensão estrutural; recuperação GraphRAG e execução operacional exigem verificações próprias.

## Flowise e Langflow

**Problema:** compor aplicações de IA com modelos, recuperação, ferramentas e fluxos visuais, mantendo clareza sobre o comportamento de cada componente.

**Decisões:** selecionar Flowise ou Langflow conforme integração, extensibilidade e operação; definir contratos dos componentes e das APIs; versionar fluxos e configurações; separar segredos do artefato; controlar acesso a ferramentas e coleções. Componentes personalizados permitem incorporar regras e integrações quando o catálogo visual não cobre o contrato necessário.

**Avaliação:** comparar entradas, documentos recuperados, chamadas de ferramentas e saídas entre versões; verificar falhas, permissões, latência e custo. A representação visual precisa permitir diagnóstico e manutenção com a mesma disciplina dos componentes escritos em código.

**Aplicação:** repertório de desenvolvimento low-code de aplicações generativas, RAG e agentes. A escolha e a implantação são específicas de cada solução; os casos não atribuem todos os frameworks a todos os projetos.

## Engenharia de dados e persistência

**Problema:** sustentar identidade, conhecimento, memória, eventos e efeitos com informação íntegra e fontes de autoridade claras.

**Decisões:** modelar entidades, chaves, relacionamentos e migrações; usar PostgreSQL/Supabase e MySQL conforme o domínio; posicionar Redis como cache ou estado temporário quando adequado. Definir transações, índices, isolamento por organização, retenção, backup e restauração. Selecionar recuperação lexical, vetorial ou híbrida conforme corpus e critérios de relevância; o índice de busca deriva da fonte e possui ciclo de atualização próprio.

**Avaliação:** consistência após falhas, concorrência, duplicidade, controle de acesso, frescura do índice e restauração do conjunto de dados. Expiração de cache, checkpoint de conversa e confirmação transacional são contratos distintos.

**Referência:** [arquitetura de dados e grafos](dados-e-grafos.md), [ledger transacional](../src/portfolio_lab/execution.py) e [recuperação com escopo](../src/portfolio_lab/retrieval.py). Os mecanismos públicos usam dados sintéticos; os bancos corporativos permanecem privados.

## Voz e telefonia — URAs cognitivas e voicebots

**Problema:** levar a capacidade de atendimento da IA ao canal telefônico, coordenando conversa, mídia, sistemas empresariais e transferência humana.

**Decisões:** definir fronteiras entre telefonia, sessão de voz e ferramentas; selecionar conversa speech-to-speech ou cadeia STT → agente → TTS conforme qualidade, latência e controle. O repertório inclui OpenAI Voice/Realtime, Google Cloud Speech-to-Text e ElevenLabs API, combinado com componentes open source como Asterisk e SIP.js. Projetar interrupção de fala, turnos, fila humana, correlação de eventos, continuidade de contexto e recuperação de falhas.

**Avaliação:** áudio bidirecional, reconhecimento de intenções críticas, latência por etapa, barge-in, silêncio, perda de conexão, transferência efetiva e confirmação no sistema de destino. Gravação, transcrição e acesso ao histórico seguem políticas explícitas de finalidade e retenção.

**Aplicação:** arquitetura e desenvolvimento da frente de voz e telefonia **no atendimento de diagnóstico por imagem**. Consulte a [arquitetura de URAs cognitivas e voicebots](voz-telefonia.md) para responsabilidades, alternativas técnicas e critérios de integração.

## Engenharia de harnesses

**Problema:** transformar comportamento esperado em evidência que permite decidir uma mudança.

**Decisões:** separar contrato, comportamento do modelo, integração e operação; definir fixtures sintéticas, casos bloqueadores e orçamento de execução; manter baseline e candidata sob condições comparáveis; identificar versões, entradas e resultados. O harness precisa declarar alvo e possíveis efeitos antes de rodar.

**Avaliação:** falha por cenário e por fatia, não apenas média; critério independente da implementação; prova de correlação no destino para ações reais. Judges baseados em LLM precisam de calibração e inspeção de discordâncias; aprovação automática sem essa análise pode mascarar erros.

**Referência:** [harness determinístico](../src/portfolio_lab/evaluate.py), [falhas transacionais](../tests/test_execution.py) e [matriz de evidências](evidencias.md). Inferência real e E2E de cliente não são inferidos desses testes.

## Engenharia de prompts e contexto

**Problema:** construir a interface entre objetivo, instrução, evidência e contrato de saída do modelo.

**Decisões:** separar instrução de conteúdo consultado; versionar templates; definir autoridade por fonte e política de conflito; controlar orçamento e truncamento; escolher exemplos representativos e saída estruturada. Contexto útil inclui também o que o sistema precisa declarar quando uma fonte está ausente ou uma operação não foi confirmada.

**Avaliação:** variações de linguagem, ambiguidade, instrução maliciosa na fonte, excesso de contexto e contradição. Prompt não substitui autorização, validação ou controle de efeitos fora do modelo.

**Referência:** [prompt demonstrativo](../src/portfolio_lab/prompts/support.md), hash nas [evidências](../evidence/evaluation.json) e contratos de resposta. O teste determinístico de fronteira não comprova resistência de um LLM a prompt injection.

## Fine-tuning

**Problema:** adaptar comportamento a uma tarefa recorrente com qualidade e economia demonstráveis.

**Decisões:** definir tarefa, taxonomia e baseline; curar exemplos e negativos; deduplicar; separar por entidade, conversa ou grupo para evitar vazamento; manter holdout fora da seleção de hiperparâmetros. Escolher SFT, ajuste completo ou adaptação eficiente como LoRA conforme modelo, tarefa, infraestrutura e custo. Rank, módulos-alvo, taxa de aprendizado e checkpoints são escolhas experimentais, não valores universais.

**Avaliação:** comparar modelo base, baseline com prompt/RAG e candidato ajustado no mesmo conjunto; medir qualidade por classe, formato, comportamento crítico, latência e custo. Promover somente com ganho relevante e ausência de regressão bloqueadora; versionar dados, modelo e adaptador para reversão.

**Referência:** [pipeline sintético de curadoria](../src/portfolio_lab/datasets.py) e [artefatos de split](../evidence/datasets/report.json). Fine-tuning é uma capacidade e frente de aplicação futura; nenhum treinamento de pesos ou ganho de modelo foi realizado neste portfólio ou atribuído aos projetos citados.

## Fontes técnicas primárias

- [SDK Python do MCP](https://github.com/modelcontextprotocol/python-sdk) e [segurança do protocolo](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices).
- [LangGraph: grafo](https://docs.langchain.com/oss/python/langgraph/graph-api) e [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts).
- [LangChain](https://docs.langchain.com/oss/python/langchain/overview), [Flowise](https://docs.flowiseai.com/) e [Langflow](https://docs.langflow.org/).
- [OpenAI Realtime](https://developers.openai.com/api/docs/guides/realtime), [Google Cloud Speech-to-Text](https://docs.cloud.google.com/speech-to-text/docs) e [ElevenLabs API](https://elevenlabs.io/docs/overview/intro).
- [Asterisk](https://docs.asterisk.org/) e [SIP.js](https://sipjs.com/guides/).
- [SQLite FTS5](https://www.sqlite.org/fts5.html).
- [Hugging Face PEFT: LoRA](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora).

As fontes documentam mecanismos. As decisões e matrizes deste dossiê são meu desenho de referência; não são certificações emitidas por essas organizações.
