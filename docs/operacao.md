# Operação, avaliação de releases e evolução

Um sistema de IA muda quando muda o modelo, o prompt, o conhecimento, uma permissão ou o contrato de um conector. Tratar apenas a versão do código como release deixa parte do comportamento fora do controle.

Este documento apresenta meu desenho de referência para operação. Os critérios abaixo são propostas de engenharia; os relatórios locais do portfólio têm escopo próprio e não comprovam esses controles em produção.

## Unidade de release

O manifesto de uma versão deve identificar código, dependências, configuração, modelo, prompt, corpus, esquema de saída e contratos das ferramentas. Segredos ficam fora do manifesto; registram-se referências de configuração, não valores. Uma fonte revisada depois da avaliação pode exigir nova verificação, mesmo sem mudança no código.

## Gates por camada

| Camada | Condição de promoção | Evidência exigida |
|---|---|---|
| Contratos | Entradas, saídas e permissões compatíveis | Testes de esquema, identidade e efeitos proibidos |
| Recuperação | Fontes corretas e escopo preservado | Conjunto de consultas rotulado, cobertura e citações |
| Modelo | Comportamento aceitável em cenários críticos | Inferência real, avaliação por fatia e revisão de divergências |
| Integração | Resultado confirmado no sistema de destino | Correlação entre operação, retorno e estado observado |
| Operação | Capacidade de observar, conter e reverter | Exercício de falha, alarmes e procedimento de recuperação |

Falha em um cenário crítico não deve ser diluída na média global. Um ganho de fluência não compensa uma ação sem autorização. O conjunto de avaliação precisa identificar cenários bloqueadores antes da execução.

## Observabilidade sem transformar logs em base sensível

Uma trilha operacional pode registrar `trace_id`, tipo de intenção, versão do contrato, fonte consultada, duração, estado de execução e motivo normalizado de falha. Texto livre, dados pessoais e payload completo exigem política específica de minimização, retenção e acesso.

Sinais que considero úteis: tempo até resolução confirmada, taxa de resultados incertos, idade da operação pendente mais antiga, latência por conector, handoff sem continuidade, volume de retries, abstenção por causa e custo por tarefa resolvida. p95/p99 precisam ser segmentados por jornada; uma média geral pode esconder falhas de um caminho transacional.

## SLOs e orçamento de erro

O indicador deve refletir o serviço percebido pela empresa. Disponibilidade do endpoint é insuficiente quando o usuário recebe uma resposta, mas a operação não se conclui. Defino evento de sucesso, janela de medição, exclusões e responsável antes de estabelecer uma meta.

Nenhum SLO numérico ou capacidade de carga é declarado neste portfólio. Metas são negociadas a partir do fluxo, risco, baseline e custo de operação.

## Mudança controlada

1. Reconciliar a versão em execução com o manifesto e a fonte de código.
2. Avaliar a candidata com os mesmos casos da baseline e as novas regressões.
3. Aplicar em ambiente isolado e verificar caminhos completos autorizados.
4. Liberar gradualmente com critérios de interrupção definidos e observação suficiente.
5. Reverter configuração/comportamento quando necessário e reconciliar efeitos já executados.

Reverter o código não desfaz uma operação externa. Compensação exige regra de negócio, autorização e identificação do efeito original.

## Procedimento para resultado incerto

Suspender repetição automática → identificar operação e versão → consultar destino por referência confiável → confirmar efeito ou ausência → decidir conclusão ou nova tentativa → registrar decisão → criar cenário de regressão. O [ledger demonstrativo](confiabilidade.md) torna parte desse procedimento inspecionável em código.

Referências: [SRE — service level objectives](https://sre.google/sre-book/service-level-objectives/), [interrupções LangGraph](https://docs.langchain.com/oss/python/langgraph/interrupts), [compensação de transações](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction).
