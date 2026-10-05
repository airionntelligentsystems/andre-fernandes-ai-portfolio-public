import pytest
from langgraph.types import Command
from pydantic import ValidationError

from portfolio_lab.contracts import Request
from portfolio_lab.retrieval import KnowledgeBase
from portfolio_lab.workflow import LocalEffects, build_workflow


@pytest.fixture
def setup():
    kb = KnowledgeBase()
    effects = LocalEffects()
    graph = build_workflow(kb, effects)
    yield kb, effects, graph
    kb.close()


def pending(graph, thread="one", query="suporte"):
    config = {"configurable": {"thread_id": thread}}
    result = graph.invoke({"request": Request(tenant="demo_alpha", query=query, intent="followup").model_dump()}, config)
    return config, result


@pytest.mark.parametrize("approve,match,expected", [(True, True, 1), (False, True, 0), (True, False, 0)])
def test_review_is_required_and_bound_to_proposal(setup, approve, match, expected):
    _, effects, graph = setup
    config, state = pending(graph)
    assert "__interrupt__" in state and not effects.entries
    digest = state["proposal_digest"] if match else "0"*64
    result = graph.invoke(Command(resume={"approved": approve, "proposal_digest": digest}), config)
    assert len(effects.entries) == expected
    assert result["status"] == ("recorded_locally" if expected else "denied")


def test_typed_decision_rejects_string_boolean_and_can_resume(setup):
    _, effects, graph = setup
    config, state = pending(graph)
    with pytest.raises(ValidationError):
        graph.invoke(Command(resume={"approved": "true", "proposal_digest": state["proposal_digest"]}), config)
    assert not effects.entries
    result = graph.invoke(Command(resume={"approved": True, "proposal_digest": state["proposal_digest"]}), config)
    assert result["status"] == "recorded_locally"


def test_duplicate_proposal_has_one_local_effect(setup):
    _, effects, graph = setup
    ids = []
    for thread in ["first", "retry"]:
        config, state = pending(graph, thread)
        result = graph.invoke(Command(resume={"approved": True, "proposal_digest": state["proposal_digest"]}), config)
        ids.append(result["operation_id"])
    assert ids[0] == ids[1] and len(effects.entries) == 1


def test_changed_scope_has_different_digest(setup):
    _, _, graph = setup
    _, first = pending(graph, "first", "suporte")
    _, second = pending(graph, "second", "cadastro")
    assert first["proposal_digest"] != second["proposal_digest"]


def test_changed_corpus_invalidates_pending_review(setup):
    kb, effects, graph = setup
    config, state = pending(graph)
    kb.version = "f"*64
    result = graph.invoke(Command(resume={"approved": True, "proposal_digest": state["proposal_digest"]}), config)
    assert result["status"] == "denied" and not effects.entries
