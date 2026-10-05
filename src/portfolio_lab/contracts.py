"""Contratos estritos nas fronteiras do laboratório."""

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Tenant = Literal["demo_alpha", "demo_beta"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Request(StrictModel):
    tenant: Tenant
    query: str = Field(min_length=1, max_length=1000)
    intent: Literal["answer", "followup"] = "answer"

    @field_validator("query")
    @classmethod
    def meaningful_query(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Consulta vazia")
        return value.strip()

    def digest(self) -> str:
        payload = json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode()).hexdigest()


class Decision(StrictModel):
    approved: bool
    proposal_digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class Source(StrictModel):
    id: str
    tenant: Tenant
    title: str
    text: str
    corpus_version: str


class Answer(StrictModel):
    status: Literal["answered", "abstained"]
    text: str
    citations: list[str]
    corpus_version: str


def validate_answer(answer: Answer, sources: list[Source], tenant: Tenant) -> None:
    """Rejeita fonte inventada, contexto cruzado e versão divergente."""
    if any(s.tenant != tenant or s.corpus_version != answer.corpus_version for s in sources):
        raise ValueError("Fonte fora do contexto ou versão divergente")
    allowed = {s.id for s in sources}
    if not set(answer.citations).issubset(allowed):
        raise ValueError("Citação não recuperada")
    if answer.status == "answered" and not answer.citations:
        raise ValueError("Resposta sem evidência")
    if answer.status == "abstained" and answer.citations:
        raise ValueError("Abstenção não deve alegar fontes utilizadas")
