import pytest

from portfolio_lab.datasets import Example, prepare, synthetic_examples
from portfolio_lab.provenance import DependencyGraph


def test_split_by_group_is_reproducible_without_leakage():
    train, validation, report = prepare(synthetic_examples())
    assert {e.group for e in train}.isdisjoint({e.group for e in validation})
    assert train and validation and not report["weights_trained"]
    assert prepare(synthetic_examples())[2] == report


def test_duplicate_content_is_removed_before_split():
    examples = synthetic_examples()
    _, _, report = prepare(examples + [examples[0]])
    assert report["input_examples"] == 13 and report["unique_examples"] == 12


def test_duplicate_with_changed_group_cannot_cross_split():
    examples = synthetic_examples()
    other = examples[0].model_copy(update={"group": "different"})
    with pytest.raises(ValueError):
        prepare(examples+[other])


def test_personal_identifier_rejected():
    examples = synthetic_examples()
    example = Example(group="contact", messages=[{"role": "system", "content": "Classifique"}, {"role": "user", "content": "Contato person@example.test"}, {"role": "assistant", "content": "encaminhar"}])
    with pytest.raises(ValueError):
        prepare(examples+[example])


def test_message_order_is_validated():
    example = Example(group="invalid", messages=[{"role": "assistant", "content": "Texto"}])
    with pytest.raises(ValueError):
        prepare([example]+synthetic_examples())


def test_graph_cycle_rejection_is_atomic_and_impact_is_transitive():
    graph = DependencyGraph()
    graph.add("corpus", "retrieval")
    graph.add("retrieval", "answer")
    graph.add("prompt", "answer")
    before = graph.snapshot()
    with pytest.raises(ValueError):
        graph.add("answer", "corpus")
    assert graph.snapshot() == before
    assert graph.descendants("corpus") == ["answer", "retrieval"]
    assert graph.descendants("prompt") == ["answer"]
