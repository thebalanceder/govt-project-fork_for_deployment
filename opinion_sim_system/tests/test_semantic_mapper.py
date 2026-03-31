from ..experiments.semantic_checks import continuity_report, decoupling_report, multi_split_stability_report
from ..models.semantic_mapper import SemanticMapper


def test_semantic_mapper_builds_unified_state() -> None:
    mapper = SemanticMapper.with_defaults()
    state = mapper.build(
        product_description="A balanced product with reliable battery and fair price.",
        comments=["battery is good", "price is fair", "setup can be confusing"],
    )

    assert -1.0 <= state.sentiment <= 1.0
    assert 0.0 <= state.stance <= 1.0
    assert abs(sum(state.topic.values()) - 1.0) < 1e-9
    assert len(state.embedding) > 0


def test_semantic_checks_return_structured_reports() -> None:
    mapper = SemanticMapper.with_defaults()
    texts = [
        "battery life is strong and stable",
        "stable battery performance and good durability",
        "support queue is long and confusing",
        "customer service is slow and disappointing",
    ]
    states = [mapper.build_for_single_text(text) for text in texts]

    similar_pairs = [(states[0], states[1]), (states[2], states[3])]
    dissimilar_pairs = [(states[0], states[2]), (states[1], states[3])]

    continuity = continuity_report(similar_pairs=similar_pairs, dissimilar_pairs=dissimilar_pairs)
    decoupling = decoupling_report(states=states)
    stability = multi_split_stability_report(states=states, n_splits=2)

    assert isinstance(continuity.passed, bool)
    assert isinstance(decoupling.passed, bool)
    assert isinstance(stability.passed, bool)
    assert continuity.similar_mean_distance <= continuity.dissimilar_mean_distance
    assert 0.0 <= decoupling.max_off_diag_correlation <= 1.0
    assert stability.n_splits == 2
