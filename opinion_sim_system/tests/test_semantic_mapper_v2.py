from ..models.semantic_mapper_v2 import SemanticMapperV2


def test_semantic_mapper_v2_builds_state_with_trace() -> None:
    mapper = SemanticMapperV2.with_defaults()
    state = mapper.build(
        product_description="A reliable product with practical design and fair value.",
        comments=[
            "great value and stable performance",
            "setup is a bit confusing",
            "价格合理，体验不错",
        ],
    )

    assert -1.0 <= state.sentiment <= 1.0
    assert 0.0 <= state.stance <= 1.0
    assert abs(sum(state.topic.values()) - 1.0) < 1e-9
    assert len(state.embedding) > 0
    assert "experts" in state.evidence_trace
    assert set(state.evidence_trace["experts"].keys()) == {
        "sentiment",
        "stance",
        "emotion",
        "topic",
        "risk",
        "value_frame",
    }


def test_semantic_mapper_v2_requires_input() -> None:
    mapper = SemanticMapperV2.with_defaults()
    try:
        mapper.build(product_description="", comments=[])
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "product_description or comments" in str(exc)
