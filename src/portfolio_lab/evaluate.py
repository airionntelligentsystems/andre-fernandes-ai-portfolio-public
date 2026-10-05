"""Harness com critérios de aceite explícitos e resultado por cenário."""

import argparse
import hashlib
import importlib.metadata
import json
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path

from langgraph.types import Command
from pydantic import ValidationError

from .contracts import Answer, Request, validate_answer
from .datasets import prepare, synthetic_examples
from .provenance import DependencyGraph
from .retrieval import KnowledgeBase, render_answer
from .workflow import LocalEffects, build_workflow


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rejects(call, error):
    try:
        call()
    except error:
        return
    raise AssertionError("Entrada deveria ter sido rejeitada")


def scenarios():
    kb = KnowledgeBase()
    cases = []

    def run(name, criterion, function):
        try:
            function()
            cases.append({"id": name, "criterion": criterion, "status": "passed"})
        except Exception as exc:
            # A evidência armazena o tipo da falha, não dados ou caminhos do ambiente.
            cases.append({"id": name, "criterion": criterion, "status": "failed", "error_type": type(exc).__name__})

    def tenant_scope():
        sources = kb.search(Request(tenant="demo_alpha", query="devolução"))
        require(bool(sources) and all(s.tenant == "demo_alpha" for s in sources), "Fonte cruzada")
        require(all("30 dias" not in s.text for s in sources), "Política Beta vazou")

    run("rag_tenant_scope", "Consulta Alpha só retorna fontes Alpha", tenant_scope)
    run("rag_unknown_abstains", "Ausência de fonte produz abstenção", lambda: require(render_answer(Request(tenant="demo_alpha", query="ornitorrinco"), [], kb.version).status == "abstained", "Resposta sem fonte"))
    run("input_extra_field", "Campo extra não muda o domínio permitido", lambda: rejects(lambda: Request.model_validate({"tenant": "demo_alpha", "query": "suporte", "admin": True}), ValidationError))
    run("citation_unknown", "Citação inventada é rejeitada", lambda: rejects(lambda: validate_answer(Answer(status="answered", text="Texto fictício", citations=["inventada"], corpus_version=kb.version), [], "demo_alpha"), ValueError))

    def query_boundary():
        req = Request(tenant="demo_alpha", query="devolução'); DROP TABLE knowledge; --")
        kb.search(req)
        require(bool(kb.search(Request(tenant="demo_alpha", query="devolução"))), "Corpus foi alterado")
    run("query_parameterization", "Texto de consulta não altera o banco", query_boundary)

    def approval(mode):
        effects = LocalEffects()
        graph = build_workflow(kb, effects)
        config = {"configurable": {"thread_id": mode}}
        request = Request(tenant="demo_alpha", query="suporte", intent="followup")
        state = graph.invoke({"request": request.model_dump()}, config)
        require("__interrupt__" in state and not effects.entries, "Efeito antes da revisão")
        digest = state["proposal_digest"] if mode != "mismatch" else "0"*64
        result = graph.invoke(Command(resume={"approved": mode != "deny", "proposal_digest": digest}), config)
        require(result["status"] == ("recorded_locally" if mode == "approve" else "denied"), "Estado incorreto")
        require(len(effects.entries) == (1 if mode == "approve" else 0), "Efeito incorreto")
        if mode == "approve":
            repeat = graph.invoke({"request": request.model_dump()}, {"configurable": {"thread_id": "repeat"}})
            graph.invoke(Command(resume={"approved": True, "proposal_digest": repeat["proposal_digest"]}), {"configurable": {"thread_id": "repeat"}})
            require(len(effects.entries) == 1, "Efeito duplicado")

    run("workflow_approval_idempotency", "Revisão antes do efeito e repetição sem duplicidade", lambda: approval("approve"))
    run("workflow_denial", "Recusa encerra sem efeito", lambda: approval("deny"))
    run("workflow_scope_binding", "Digest divergente não autoriza efeito", lambda: approval("mismatch"))

    def graph_cycle():
        graph = DependencyGraph()
        graph.add("corpus", "retrieval")
        graph.add("retrieval", "answer")
        before = graph.snapshot()
        rejects(lambda: graph.add("answer", "corpus"), ValueError)
        require(graph.snapshot() == before and graph.descendants("corpus") == ["answer", "retrieval"], "Proveniência inválida")
    run("graph_cycle_impact", "Ciclo rejeitado sem mutação e impacto rastreável", graph_cycle)

    def dataset_split():
        train, validation, report = prepare(synthetic_examples())
        require(bool(train) and bool(validation), "Partição vazia")
        require(not ({e.group for e in train} & {e.group for e in validation}), "Grupo cruzado")
        require(not report["weights_trained"], "Alegação de treinamento incorreta")
    run("fine_tuning_group_split", "Grupos não se cruzam e treinamento não é alegado", dataset_split)

    report = {"scope": "contratos determinísticos e SDK LangGraph em cenário fictício", "llm_executed": False, "production_validated": False, "generated_at": datetime.now(timezone.utc).isoformat(), "versions": {name: importlib.metadata.version(name) for name in ["langgraph", "mcp", "pydantic"]}, "corpus_sha256": kb.version, "prompt_sha256": hashlib.sha256(files("portfolio_lab").joinpath("prompts/support.md").read_bytes()).hexdigest(), "scenarios": cases, "passed": sum(c["status"] == "passed" for c in cases), "total": len(cases)}
    kb.close()
    return report


def main():
    parser = argparse.ArgumentParser(description="Avaliar contratos do laboratório fictício")
    parser.add_argument("--output", type=Path, default=Path("evidence/evaluation.json"))
    args = parser.parse_args()
    report = scenarios()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "total": report["total"], "llm_executed": False}))
    raise SystemExit(0 if report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    main()
