from ..experiments.semantic_checks import decoupling_report, multi_split_stability_report
from ..models.semantic_state import SemanticState


def _state(sentiment: float, stance: float, topic_a: float, emb: list[float]) -> SemanticState:
    return SemanticState(
        sentiment=sentiment,
        stance=stance,
        topic={"topic_0": topic_a, "topic_1": 1.0 - topic_a},
        embedding=emb,
    )


def test_decoupling_report_uses_informative_embedding_features() -> None:
    states = [
        _state(-0.7, 0.1, 0.8, [0.9, 0.1, -0.2, 0.0]),
        _state(-0.2, 0.3, 0.7, [0.7, -0.2, 0.4, 0.1]),
        _state(0.1, 0.5, 0.4, [0.3, 0.6, -0.1, 0.2]),
        _state(0.6, 0.7, 0.3, [-0.2, 0.8, 0.2, 0.3]),
        _state(0.8, 0.9, 0.2, [-0.5, 0.4, 0.6, -0.1]),
    ]

    report = decoupling_report(states=states, threshold=0.99)
    assert 0.0 <= report.max_off_diag_correlation <= 1.0
    assert report.passed is True


def test_multi_split_stability_reports_split_count() -> None:
    states = [
        _state(-0.4, 0.3, 0.7, [0.4, 0.1, -0.2, 0.3]),
        _state(-0.3, 0.35, 0.68, [0.38, 0.12, -0.18, 0.31]),
        _state(0.2, 0.55, 0.45, [0.2, 0.3, 0.1, -0.2]),
        _state(0.25, 0.58, 0.43, [0.19, 0.31, 0.12, -0.19]),
        _state(0.6, 0.75, 0.25, [-0.1, 0.4, 0.2, 0.1]),
        _state(0.58, 0.73, 0.27, [-0.11, 0.39, 0.18, 0.09]),
    ]

    report = multi_split_stability_report(states=states, n_splits=3, tolerance=0.3)
    assert report.n_splits == 3
    assert isinstance(report.passed, bool)
