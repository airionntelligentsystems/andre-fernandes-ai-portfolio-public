# Evidências e critérios de leitura

| Tipo | Fonte | O que permite concluir |
|---|---|---|
| Projetos profissionais reais | Atuação profissional, relatos de André e documentação/configurações conforme a fonte identificada em cada caso | Contexto, escopo de desenvolvimento, decisões e responsabilidades descritas nos estudos de caso |
| Código demonstrativo | Código e testes deste repositório | Estrutura, contratos e comportamento do laboratório |
| Execução local | Relatórios em `evidence/` | Cenários observados com as versões registradas |
| CI remota | Execuções do GitHub Actions | Resultado no ambiente remoto de cada execução |

Saúde e hotelaria são projetos profissionais reais de desenvolvimento e integração; a plataforma de serviços é um produto real em desenvolvimento. O escopo da solução de hotelaria foi confirmado diretamente por André em 05/10/2026: IA para reservas e suporte durante estadias, integrada a CRM, marketing e gestão. Os casos não são simulações do laboratório. As fontes profissionais e a revisão de documentação não constituem auditoria atual de produção nem comprovam métricas comerciais.

| Projeto ou frente | Base da descrição e estágio apresentado |
|---|---|
| Inteligência no agronegócio | Apresentação existente do produto e materiais de desenvolvimento consultados; arquitetura multiagente e escopo funcional de inteligência setorial |
| Jornada hospitalar | README e configuração da aplicação consultados; desenvolvimento de experiência funcional e contratos de integração |
| Plataformas corporativas próprias | READMEs, configurações e estrutura de módulos consultados; gestão modular, suporte com agentes e jornada hospitalar com estágio específico em cada síntese |
| Voz e telefonia em saúde | Confirmação de André e documentação do projeto de voz e telefonia consultadas; arquitetura e desenvolvimento de componentes de telefonia, agentes, ferramentas e continuidade humana |
| LangChain, Flowise, Langflow e APIs de voz | Repertório indicado por André e papéis conferidos em documentação primária; a inclusão não atribui implantação de todas as tecnologias a todos os casos |
| Graphify e dados | Estrutura e documentação do projeto de saúde consultadas; mapa técnico, persistência e responsabilidades arquiteturais |

As fontes foram consultadas em 05/10/2026. A apresentação preserva os estágios das entregas e limita a divulgação a sínteses profissionais e abstrações técnicas.

Os relatórios técnicos públicos são provas das implementações independentes, sem estabelecer resultados de clientes. Execução local e CI são fontes distintas; a existência de um workflow não significa que ele tenha passado. O hash do corpus e do prompt identifica as entradas avaliadas. O fine-tuning aqui cobre preparação dos dados; não há treinamento ou comparação de modelos executada.

Para reproduzir, execute os comandos do README. Os arquivos em `evidence/` são gerados pelo laboratório; não são relatórios comerciais nem resultados simulados apresentados como reais.

Design conversacional, Discovery/Design Thinking, microcopy/acessibilidade, métricas, homologação com Desenvolvimento/QA, Blip/Manychat e canais adicionais foram confirmados diretamente por André em 05/10/2026. Consulte [design conversacional](design-conversacional.md). Essas declarações descrevem experiência profissional; não são auditoria externa de resultados.
