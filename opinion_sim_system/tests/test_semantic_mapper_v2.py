from ..models.semantic_mapper_v2 import SemanticMapperV2
from ..models.task_experts import InputCase


def test_semantic_mapper_v2_builds_state_with_trace() -> None:
    mapper = SemanticMapperV2.with_defaults()
    state = mapper.build(
        product_description="A reliable product with practical design and fair value.",
        target="smart-home product",
        domain="product",
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
        "acceptance",
        "emotion",
        "topic",
        "conflict",
        "frame",
        "stance",
        "risk",
        "value_frame",
    }
    assert "consensus" in state.evidence_trace.get("fusion", {})
    consensus = state.evidence_trace["fusion"]["consensus"]
    assert 0.0 <= consensus["score"] <= 1.0
    assert consensus["method"] in {"average", "deepseek", "fallback-average"}


def test_semantic_mapper_v2_requires_input() -> None:
    mapper = SemanticMapperV2.with_defaults()
    try:
        mapper.build(product_description="", comments=[])
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "product_description or comments" in str(exc)


def test_semantic_mapper_v2_build_from_input_case() -> None:
    mapper = SemanticMapperV2.with_defaults()
    state = mapper.build_from_case(
        case=InputCase(
            text="Policy proposal focused on fairness and service quality.",
            target="city service policy",
            domain="policy",
        ),
        comments=[
            "this policy is fair and practical",
            "implementation risk should be considered",
            "communication needs more clarity",
        ],
    )

    assert -1.0 <= state.sentiment <= 1.0
    assert 0.0 <= state.stance <= 1.0
    assert len(state.embedding) > 0
    experts = state.evidence_trace.get("experts", {})
    assert "acceptance" in experts
    assert "conflict" in experts
    assert "frame" in experts
