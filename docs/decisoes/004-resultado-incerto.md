# Decisão 004 — resultado incerto exige reconciliação

**Contexto:** uma chamada externa pode ter sido aceita antes da perda de conexão ou da queda do worker. A operação precisa sobreviver ao reinício sem repetir o efeito de forma indiscriminada.

**Alternativas:** repetir após todo timeout; manter apenas um indicador em memória; persistir a intenção com reserva e tratar a incerteza como estado próprio.

**Decisão:** usar ledger persistente, chave vinculada ao conteúdo, reserva exclusiva e estado `uncertain`. Confirmação exige correlação; nova tentativa após incerteza exige observação confiável de ausência de efeito.

**Consequências:** persistência e auditoria ficam no mesmo domínio transacional. O worker vencido não pode concluir uma reserva. O processamento pode parar para reconciliação; essa interrupção é preferível a duplicar uma ação. O controle local não promete entrega externa exatamente uma vez.

**Prova:** [implementação](../../src/portfolio_lab/execution.py) e [testes](../../tests/test_execution.py). O destino é sintético; identidade, transporte e autenticidade do recibo não são implementados.
