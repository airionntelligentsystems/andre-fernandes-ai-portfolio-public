"""Ledger/outbox local durável; não contém transporte ou autenticação remota."""

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from typing import Literal
from uuid import uuid4

from pydantic import Field, TypeAdapter

from .contracts import StrictModel

Tenant = Literal["demo_alpha", "demo_beta"]
TENANT = TypeAdapter(Tenant)


class Operation(StrictModel):
    tenant: Tenant
    key: str = Field(pattern=r"^[a-z0-9_-]{1,80}$")
    kind: Literal["followup"] = "followup"
    text: str = Field(min_length=1, max_length=1000)
    policy_version: str = Field(min_length=1, max_length=80)

    def canonical(self) -> str:
        return json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    def digest(self) -> str:
        return hashlib.sha256(self.canonical().encode()).hexdigest()


class Receipt(StrictModel):
    tenant: Tenant
    key: str = Field(pattern=r"^[a-z0-9_-]{1,80}$")
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    reference: str = Field(min_length=1, max_length=80)


@dataclass(frozen=True)
class Claim:
    tenant: str
    key: str
    digest: str
    token: str
    expires_at: float
    operation: Operation


class Conflict(ValueError):
    """Estado, conteúdo ou confirmação incompatível com a intenção persistida."""


class ExecutionLedger:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(path, timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS operations (
                tenant TEXT NOT NULL, key TEXT NOT NULL, digest TEXT NOT NULL,
                payload TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN
                    ('prepared','ready','inflight','uncertain','confirmed')),
                reviewer TEXT, token TEXT, expires_at REAL, reference TEXT,
                attempts INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (tenant, key)
            );
            CREATE TABLE IF NOT EXISTS events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant TEXT NOT NULL, key TEXT NOT NULL,
                kind TEXT NOT NULL, digest TEXT NOT NULL
            );
        """)

    def close(self):
        self.db.close()

    @contextmanager
    def _transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def _event(self, tenant: str, key: str, kind: str, digest: str):
        # Auditoria de transições; nenhum conteúdo de mensagem no evento.
        self.db.execute("INSERT INTO events(tenant,key,kind,digest) VALUES(?,?,?,?)", (tenant, key, kind, digest))

    def get(self, tenant: Tenant, key: str) -> dict:
        TENANT.validate_python(tenant, strict=True)
        row = self.db.execute("SELECT * FROM operations WHERE tenant=? AND key=?", (tenant, key)).fetchone()
        if row is None:
            raise Conflict("Operação inexistente no escopo")
        return dict(row)

    def prepare(self, operation: Operation) -> str:
        digest = operation.digest()
        with self._transaction():
            old = self.db.execute("SELECT digest FROM operations WHERE tenant=? AND key=?", (operation.tenant, operation.key)).fetchone()
            if old:
                if old["digest"] != digest:
                    raise Conflict("Chave reutilizada com conteúdo ou política diferentes")
                return digest
            self.db.execute("INSERT INTO operations(tenant,key,digest,payload,status) VALUES(?,?,?,?,'prepared')", (operation.tenant, operation.key, digest, operation.canonical()))
            self._event(operation.tenant, operation.key, "prepared", digest)
        return digest

    def approve(self, tenant: Tenant, key: str, digest: str, reviewer: str):
        # reviewer identifica o ator informado pelo chamador; não o autentica.
        if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 80:
            raise ValueError("Revisor inválido")
        with self._transaction():
            row = self.get(tenant, key)
            if row["digest"] != digest or row["status"] != "prepared":
                raise Conflict("Aprovação não corresponde à proposta pendente")
            self.db.execute("UPDATE operations SET status='ready', reviewer=? WHERE tenant=? AND key=?", (reviewer, tenant, key))
            self._event(tenant, key, "approved", digest)

    def claim(self, tenant: Tenant, *, now: float, ttl: float = 30) -> Claim | None:
        TENANT.validate_python(tenant, strict=True)
        if not math.isfinite(now) or not math.isfinite(ttl) or ttl <= 0:
            raise ValueError("Prazo inválido")
        with self._transaction():
            expired = self.db.execute("SELECT key,digest FROM operations WHERE tenant=? AND status='inflight' AND expires_at<=?", (tenant, now)).fetchall()
            for row in expired:
                self.db.execute("UPDATE operations SET status='uncertain', token=NULL WHERE tenant=? AND key=?", (tenant, row["key"]))
                self._event(tenant, row["key"], "lease_expired", row["digest"])
            row = self.db.execute("SELECT * FROM operations WHERE tenant=? AND status='ready' ORDER BY key LIMIT 1", (tenant,)).fetchone()
            if row is None:
                return None
            token, deadline = uuid4().hex, now + ttl
            if not math.isfinite(deadline):
                raise ValueError("Prazo fora do intervalo")
            self.db.execute("UPDATE operations SET status='inflight', token=?, expires_at=?, attempts=attempts+1 WHERE tenant=? AND key=?", (token, deadline, tenant, row["key"]))
            self._event(tenant, row["key"], "claimed", row["digest"])
            return Claim(tenant, row["key"], row["digest"], token, deadline, Operation.model_validate_json(row["payload"]))

    @staticmethod
    def _correlate(row: dict, receipt: Receipt):
        if (row["tenant"], row["key"], row["digest"]) != (receipt.tenant, receipt.key, receipt.digest):
            raise Conflict("Confirmação não correlacionada")

    def confirm(self, claim: Claim, receipt: Receipt, *, now: float):
        if not math.isfinite(now):
            raise ValueError("Relógio inválido")
        with self._transaction():
            row = self.get(claim.tenant, claim.key)
            if row["status"] != "inflight" or row["token"] != claim.token or row["expires_at"] <= now:
                raise Conflict("Reserva inválida ou expirada")
            self._correlate(row, receipt)
            self.db.execute("UPDATE operations SET status='confirmed', reference=?, token=NULL WHERE tenant=? AND key=?", (receipt.reference, claim.tenant, claim.key))
            self._event(claim.tenant, claim.key, "confirmed", row["digest"])

    def reconcile(self, tenant: Tenant, key: str, *, found: bool, receipt: Receipt | None = None):
        # Chamador confiável deve obter found da fonte operacional, não do LLM.
        if type(found) is not bool:
            raise ValueError("Observação deve ser booleana estrita")
        with self._transaction():
            row = self.get(tenant, key)
            if row["status"] != "uncertain":
                raise Conflict("Operação não aguarda reconciliação")
            if found:
                if receipt is None:
                    raise Conflict("Efeito encontrado sem recibo")
                self._correlate(row, receipt)
                status, reference, event = "confirmed", receipt.reference, "reconciled_confirmed"
            else:
                if receipt is not None:
                    raise Conflict("Ausência de efeito contradiz o recibo")
                status, reference, event = "ready", None, "reconciled_absent"
            self.db.execute("UPDATE operations SET status=?, reference=?, token=NULL, expires_at=NULL WHERE tenant=? AND key=?", (status, reference, tenant, key))
            self._event(tenant, key, event, row["digest"])

    def events(self, tenant: Tenant, key: str) -> list[str]:
        TENANT.validate_python(tenant, strict=True)
        return [r[0] for r in self.db.execute("SELECT kind FROM events WHERE tenant=? AND key=? ORDER BY sequence", (tenant, key))]
