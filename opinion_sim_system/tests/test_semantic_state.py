from ..models.semantic_state import SemanticState


def test_semantic_state_clamps_and_normalizes() -> None:
    state = SemanticState(
        sentiment=1.6,
        stance=-0.2,
        topic={"topic_a": 2.0, "topic_b": 1.0},
        embedding=[1.0, 2.0, 3.0],
    )

    assert state.sentiment == 1.0
    assert state.stance == 0.0
    assert abs(sum(state.topic.values()) - 1.0) < 1e-9


def test_semantic_state_requires_embedding() -> None:
    try:
        SemanticState(sentiment=0.0, stance=0.5, topic={"topic_0": 1.0}, embedding=[])
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "embedding" in str(exc)
