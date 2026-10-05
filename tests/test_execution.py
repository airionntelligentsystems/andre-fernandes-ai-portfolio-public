from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier

import pytest

from portfolio_lab.execution import Conflict, ExecutionLedger, Operation, Receipt


def operation(**changes):
    return Operation(tenant="demo_alpha", key="task-1", text="Mensagem fictícia de continuidade B2B", policy_version="demo-v1").model_copy(update=changes)


@pytest.fixture
def ledger(tmp_path):
    obj = ExecutionLedger(tmp_path/"execution.sqlite")
    yield obj
    obj.close()


def ready(ledger, op=None):
    op = op or operation()
    digest = ledger.prepare(op)
    ledger.approve(op.tenant, op.key, digest, "demo-reviewer")
    return op


def receipt(claim, **changes):
    return Receipt(tenant=claim.tenant, key=claim.key, digest=claim.digest, reference="synthetic-ack").model_copy(update=changes)


def test_idempotency_and_approval_boundary(ledger):
    op = operation()
    digest = ledger.prepare(op)
    assert ledger.prepare(op) == digest
    assert ledger.events(op.tenant, op.key) == ["prepared"]
    assert ledger.claim(op.tenant, now=0) is None
    with pytest.raises(Conflict):
        ledger.approve(op.tenant, op.key, "0"*64, "demo-reviewer")
    assert ledger.get(op.tenant, op.key)["status"] == "prepared"


@pytest.mark.parametrize("changes", [{"text": "Outra mensagem fictícia"}, {"policy_version": "demo-v2"}])
def test_same_key_different_intent_conflicts(ledger, changes):
    ledger.prepare(operation())
    with pytest.raises(Conflict):
        ledger.prepare(operation(**changes))


def test_restart_preserves_state_and_event(tmp_path):
    path = tmp_path/"persistent.sqlite"
    first = ExecutionLedger(path)
    op = ready(first)
    first.close()
    second = ExecutionLedger(path)
    try:
        claim = second.claim(op.tenant, now=10)
        second.confirm(claim, receipt(claim), now=11)
        assert second.get(op.tenant, op.key)["status"] == "confirmed"
        assert second.events(op.tenant, op.key) == ["prepared", "approved", "claimed", "confirmed"]
    finally:
        second.close()


def test_two_connections_compete_for_one_claim(tmp_path):
    path = tmp_path/"concurrent.sqlite"
    setup = ExecutionLedger(path)
    ready(setup)
    setup.close()
    barrier = Barrier(2)

    def worker():
        local = ExecutionLedger(path)
        try:
            barrier.wait(timeout=5)
            return local.claim("demo_alpha", now=10)
        finally:
            local.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(worker) for _ in range(2)]
        results = [future.result(timeout=10) for future in futures]
    assert sum(value is not None for value in results) == 1


def test_tenant_boundaries(ledger):
    alpha = ready(ledger)
    assert ledger.claim("demo_beta", now=0) is None
    with pytest.raises(Conflict):
        ledger.get("demo_beta", alpha.key)
    beta = ready(ledger, operation(tenant="demo_beta"))
    assert ledger.claim(beta.tenant, now=0).tenant == "demo_beta"
    assert ledger.get(alpha.tenant, alpha.key)["status"] == "ready"


def test_receipt_and_worker_must_match(ledger):
    ready(ledger)
    claim = ledger.claim("demo_alpha", now=0)
    for wrong in [receipt(claim, tenant="demo_beta"), receipt(claim, key="task-2"), receipt(claim, digest="0"*64)]:
        with pytest.raises(Conflict):
            ledger.confirm(claim, wrong, now=1)
    with pytest.raises(Conflict):
        ledger.confirm(replace(claim, token="old-worker"), receipt(claim), now=1)
    assert ledger.get(claim.tenant, claim.key)["status"] == "inflight"


def test_expired_claim_never_redrives_automatically(ledger):
    ready(ledger)
    claim = ledger.claim("demo_alpha", now=0, ttl=5)
    with pytest.raises(Conflict):
        ledger.confirm(claim, receipt(claim), now=5)
    assert ledger.claim("demo_alpha", now=5) is None
    assert ledger.get(claim.tenant, claim.key)["status"] == "uncertain"
    ledger.reconcile(claim.tenant, claim.key, found=True, receipt=receipt(claim))
    assert ledger.get(claim.tenant, claim.key)["status"] == "confirmed"
    assert ledger.claim("demo_alpha", now=6) is None


def test_confirmed_absence_allows_new_claim_and_fences_old_worker(ledger):
    ready(ledger)
    old = ledger.claim("demo_alpha", now=0, ttl=5)
    ledger.claim("demo_alpha", now=5)
    ledger.reconcile(old.tenant, old.key, found=False)
    new = ledger.claim("demo_alpha", now=6)
    assert new.token != old.token
    with pytest.raises(Conflict):
        ledger.confirm(old, receipt(old), now=7)
    ledger.confirm(new, receipt(new), now=7)
    assert ledger.get(new.tenant, new.key)["attempts"] == 2


def test_reconciliation_rejects_contradictory_observations(ledger):
    ready(ledger)
    claim = ledger.claim("demo_alpha", now=0, ttl=5)
    ledger.claim("demo_alpha", now=5)
    for kwargs in [{"found": True}, {"found": False, "receipt": receipt(claim)}, {"found": "false"}, {"found": True, "receipt": receipt(claim, tenant="demo_beta")}]:
        with pytest.raises((Conflict, ValueError)):
            ledger.reconcile(claim.tenant, claim.key, **kwargs)
    assert ledger.get(claim.tenant, claim.key)["status"] == "uncertain"


def test_audit_failure_rolls_back_state_and_event(ledger, monkeypatch):
    op = operation()
    ledger.prepare(op)
    def fail(*args):
        raise RuntimeError("Falha sintética na auditoria")
    monkeypatch.setattr(ledger, "_event", fail)
    with pytest.raises(RuntimeError):
        ledger.approve(op.tenant, op.key, op.digest(), "demo-reviewer")
    assert ledger.get(op.tenant, op.key)["status"] == "prepared"
    assert ledger.events(op.tenant, op.key) == ["prepared"]
