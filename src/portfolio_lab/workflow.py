"""LangGraph com interrupção, revisão vinculada e efeito fictício idempotente."""

import hashlib
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from .contracts import Decision, Request, Source
from .retrieval import KnowledgeBase, render_answer


class State(TypedDict, total=False):
    request: dict
    sources: list[dict]
    proposal_digest: str
    status: str
    answer: dict
    operation_id: str


class LocalEffects:
    """Registro em memória; não envia nem grava em um serviço externo."""
    def __init__(self):
        self.entries: dict[str, str] = {}

    def record(self, proposal_digest: str) -> str:
        return self.entries.setdefault(proposal_digest, f"demo-{proposal_digest[:12]}")


def build_workflow(kb: KnowledgeBase, effects: LocalEffects):
    def digest(request: Request) -> str:
        return hashlib.sha256(f"{request.digest()}:{kb.version}".encode()).hexdigest()

    def retrieve(state: State):
        req = Request.model_validate(state["request"])
        return {"sources": [s.model_dump() for s in kb.search(req)]}

    def answer(state: State):
        req = Request.model_validate(state["request"])
        result = render_answer(req, [Source.model_validate(s) for s in state["sources"]], kb.version)
        return {"answer": result.model_dump(), "status": result.status}

    def propose(state: State):
        req = Request.model_validate(state["request"])
        # A versão participa do vínculo entre intenção e decisão.
        return {"proposal_digest": digest(req), "status": "awaiting_review"}

    def review(state: State):
        decision = interrupt(
            {"proposal_digest": state["proposal_digest"], "tenant": state["request"]["tenant"], "effect": "registro fictício local"},
            response_schema=Decision,
        )
        current_digest = digest(Request.model_validate(state["request"]))
        approved = decision.approved and decision.proposal_digest == state["proposal_digest"] == current_digest
        return {"status": "approved" if approved else "denied"}

    def record(state: State):
        return {"operation_id": effects.record(state["proposal_digest"]), "status": "recorded_locally"}

    graph = StateGraph(State)
    for name, node in [("retrieve", retrieve), ("answer", answer), ("propose", propose), ("review", review), ("record", record)]:
        graph.add_node(name, node)
    graph.add_edge(START, "retrieve")
    graph.add_conditional_edges("retrieve", lambda s: s["request"].get("intent", "answer"), {"answer": "answer", "followup": "propose"})
    graph.add_edge("answer", END)
    graph.add_edge("propose", "review")
    graph.add_conditional_edges("review", lambda s: s["status"], {"approved": "record", "denied": END})
    graph.add_edge("record", END)
    return graph.compile(checkpointer=InMemorySaver())
