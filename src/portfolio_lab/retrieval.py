"""Baseline lexical FTS5 com contexto, versão e resposta extrativa."""

import hashlib
import json
import re
import sqlite3
from importlib.resources import files

from .contracts import Answer, Request, Source, validate_answer


class KnowledgeBase:
    def __init__(self, documents: list[dict] | None = None):
        if documents is None:
            documents = json.loads(files("portfolio_lab").joinpath("data/knowledge.json").read_text(encoding="utf-8"))
        self.version = hashlib.sha256(json.dumps(documents, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.execute("CREATE VIRTUAL TABLE knowledge USING fts5(id UNINDEXED, tenant UNINDEXED, title, text, tokenize='unicode61 remove_diacritics 2')")
        self.db.executemany("INSERT INTO knowledge VALUES (?, ?, ?, ?)", [(d["id"], d["tenant"], d["title"], d["text"]) for d in documents])

    def search(self, request: Request, limit: int = 3) -> list[Source]:
        if not 1 <= limit <= 5:
            raise ValueError("Limite deve estar entre 1 e 5")
        # O texto livre nunca se torna SQL ou sintaxe FTS fornecida pelo chamador.
        tokens = re.findall(r"\w+", request.query.lower(), re.UNICODE)
        tokens = [t for t in tokens if len(t) > 2 and t not in {"qual", "para", "como", "uma", "dos", "das", "que"}]
        if not tokens:
            return []
        expression = " OR ".join(f'"{t}"' for t in tokens[:50])
        rows = self.db.execute(
            "SELECT id, tenant, title, text FROM knowledge WHERE knowledge MATCH ? AND tenant = ? ORDER BY bm25(knowledge), id LIMIT ?",
            (expression, request.tenant, limit),
        ).fetchall()
        return [Source(id=i, tenant=tenant, title=title, text=text, corpus_version=self.version) for i, tenant, title, text in rows]

    def close(self) -> None:
        self.db.close()


def render_answer(request: Request, sources: list[Source], corpus_version: str) -> Answer:
    if sources:
        answer = Answer(status="answered", text="\n".join(f"[{s.id}] {s.text}" for s in sources), citations=[s.id for s in sources], corpus_version=corpus_version)
    else:
        answer = Answer(status="abstained", text="Não há fonte suficiente no contexto demonstrativo para responder.", citations=[], corpus_version=corpus_version)
    validate_answer(answer, sources, request.tenant)
    return answer
