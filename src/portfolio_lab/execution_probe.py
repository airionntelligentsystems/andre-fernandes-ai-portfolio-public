"""Experimentos locais de persistência e recuperação, sem despacho externo."""

import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from .execution import Conflict, ExecutionLedger, Operation, Receipt


def run() -> dict:
    results = []
    with TemporaryDirectory() as directory:
        path = Path(directory)/"synthetic.sqlite"
        with closing(ExecutionLedger(path)) as ledger:
            op = Operation(tenant="demo_alpha", key="followup-1", text="Continuidade B2B fictícia", policy_version="demo-v1")
            digest = ledger.prepare(op)
            if ledger.claim(op.tenant, now=0) is not None:
                raise RuntimeError("Execução antes da aprovação")
            results.append({"scenario": "aprovação antes da reserva", "passed": True})
            ledger.approve(op.tenant, op.key, digest, "demo-reviewer")

        with closing(ExecutionLedger(path)) as restarted:
            claim = restarted.claim(op.tenant, now=10, ttl=5)
            if claim is None or claim.digest != digest:
                raise RuntimeError("Estado não preservado após reinício")
            results.append({"scenario": "reinício com intenção e aprovação preservadas", "passed": True})
            if restarted.claim(op.tenant, now=15) is not None or restarted.get(op.tenant, op.key)["status"] != "uncertain":
                raise RuntimeError("Resultado incerto repetido automaticamente")
            results.append({"scenario": "reserva expirada entra em reconciliação", "passed": True})
            restarted.reconcile(op.tenant, op.key, found=False)
            new_claim = restarted.claim(op.tenant, now=16)
            if new_claim is None or new_claim.token == claim.token:
                raise RuntimeError("Nova reserva inválida")
            ack = Receipt(tenant=op.tenant, key=op.key, digest=digest, reference="synthetic-receipt")
            try:
                restarted.confirm(claim, ack, now=17)
            except Conflict:
                results.append({"scenario": "worker antigo impedido de concluir", "passed": True})
            else:
                raise RuntimeError("Worker antigo aceito")
            restarted.confirm(new_claim, ack, now=17)
            if restarted.get(op.tenant, op.key)["status"] != "confirmed":
                raise RuntimeError("Recibo correlacionado não registrado")
            results.append({"scenario": "nova tentativa após ausência observada e recibo sintético", "passed": True})
            events = restarted.events(op.tenant, op.key)
    return {"scope": "experimentos locais com ledger SQLite e destino sintético", "generated_at": datetime.now(timezone.utc).isoformat(), "passed": len(results), "total": 5, "scenarios": results, "events": events, "external_dispatch_executed": False, "provider_ack_verified": False, "authentication_implemented": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "total": report["total"], "external_dispatch_executed": False}))


if __name__ == "__main__":
    main()
