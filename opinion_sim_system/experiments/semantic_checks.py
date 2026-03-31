"""Semantic continuity/decoupling/stability checks for phase1.1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np

from ..models.semantic_mapper import cosine_distance
from ..models.semantic_state import SemanticState


def _topic_l1_distance(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a) | set(b)
    return 0.5 * sum(abs(a.get(key, 0.0) - b.get(key, 0.0)) for key in keys)


def semantic_state_distance(a: SemanticState, b: SemanticState) -> float:
    emb_dist = cosine_distance(a.embedding, b.embedding)
    sentiment_dist = abs(a.sentiment - b.sentiment) / 2.0
    stance_dist = abs(a.stance - b.stance)
    topic_dist = _topic_l1_distance(a.topic, b.topic)
    return 0.5 * emb_dist + 0.2 * sentiment_dist + 0.15 * stance_dist + 0.15 * topic_dist


@dataclass(slots=True)
class ContinuityReport:
    similar_mean_distance: float
    dissimilar_mean_distance: float
    passed: bool


def continuity_report(
    similar_pairs: list[tuple[SemanticState, SemanticState]],
    dissimilar_pairs: list[tuple[SemanticState, SemanticState]],
) -> ContinuityReport:
    if not similar_pairs or not dissimilar_pairs:
        return ContinuityReport(0.0, 0.0, False)

    sim_dist = [semantic_state_distance(a, b) for a, b in similar_pairs]
    dis_dist = [semantic_state_distance(a, b) for a, b in dissimilar_pairs]
    sim_mean = float(sum(sim_dist) / len(sim_dist))
    dis_mean = float(sum(dis_dist) / len(dis_dist))
    passed = sim_mean < dis_mean
    return ContinuityReport(similar_mean_distance=sim_mean, dissimilar_mean_distance=dis_mean, passed=passed)


@dataclass(slots=True)
class DecouplingReport:
    max_off_diag_correlation: float
    passed: bool


def decoupling_report(states: list[SemanticState], threshold: float = 0.98) -> DecouplingReport:
    if len(states) < 3:
        return DecouplingReport(max_off_diag_correlation=0.0, passed=False)

    emb_width = min(3, len(states[0].embedding))
    features = np.asarray(
        [
            (
                item.sentiment,
                item.stance,
                max(item.topic.values()) if item.topic else 0.0,
                *[float(component) for component in item.embedding[:emb_width]],
            )
            for item in states
        ],
        dtype=np.float64,
    )

    if features.ndim != 2:
        return DecouplingReport(max_off_diag_correlation=1.0, passed=False)

    std = np.std(features, axis=0)
    keep = std >= 1e-12
    # Need at least two effective dimensions for correlation structure.
    if int(np.sum(keep)) < 2:
        return DecouplingReport(max_off_diag_correlation=1.0, passed=False)
    features = features[:, keep]

    corr = np.asarray(np.corrcoef(features, rowvar=False), dtype=np.float64)
    if corr.ndim != 2:
        return DecouplingReport(max_off_diag_correlation=1.0, passed=False)

    rows = int(corr.shape[0])
    cols = int(corr.shape[1])
    max_corr = 0.0
    for i in range(rows):
        for j in range(cols):
            if i == j:
                continue
            value = abs(float(corr[i, j]))
            if not math.isnan(value):
                max_corr = max(max_corr, value)

    return DecouplingReport(max_off_diag_correlation=max_corr, passed=max_corr <= threshold)


@dataclass(slots=True)
class StabilityReport:
    sentiment_mean_delta: float
    stance_mean_delta: float
    topic_l1_delta: float
    embedding_cosine_distance: float
    n_splits: int
    passed: bool


def _batch_stats(states: list[SemanticState]) -> tuple[float, float, dict[str, float], list[float]]:
    sentiment_mean = float(sum(item.sentiment for item in states) / len(states))
    stance_mean = float(sum(item.stance for item in states) / len(states))

    topic_keys = set().union(*(item.topic.keys() for item in states))
    topic_mean = {
        key: float(sum(item.topic.get(key, 0.0) for item in states) / len(states))
        for key in sorted(topic_keys)
    }

    matrix = np.asarray([item.embedding for item in states], dtype=np.float64)
    emb_mean = matrix.mean(axis=0)
    norm = float(np.linalg.norm(emb_mean))
    if norm > 0:
        emb_mean = emb_mean / norm
    return sentiment_mean, stance_mean, topic_mean, [float(item) for item in emb_mean.tolist()]


def cross_batch_stability_report(
    batch_a: list[SemanticState],
    batch_b: list[SemanticState],
    tolerance: float = 0.2,
) -> StabilityReport:
    if not batch_a or not batch_b:
        return StabilityReport(0.0, 0.0, 0.0, 0.0, 0, False)

    a_sent, a_stance, a_topic, a_emb = _batch_stats(batch_a)
    b_sent, b_stance, b_topic, b_emb = _batch_stats(batch_b)

    sent_delta = abs(a_sent - b_sent)
    stance_delta = abs(a_stance - b_stance)
    topic_delta = _topic_l1_distance(a_topic, b_topic)
    emb_delta = cosine_distance(a_emb, b_emb)
    passed = max(sent_delta, stance_delta, topic_delta, emb_delta) <= tolerance
    return StabilityReport(
        sentiment_mean_delta=sent_delta,
        stance_mean_delta=stance_delta,
        topic_l1_delta=topic_delta,
        embedding_cosine_distance=emb_delta,
        n_splits=1,
        passed=passed,
    )


def multi_split_stability_report(
    states: list[SemanticState],
    n_splits: int = 3,
    tolerance: float = 0.2,
) -> StabilityReport:
    if len(states) < 4 or n_splits <= 0:
        return StabilityReport(0.0, 0.0, 0.0, 0.0, 0, False)

    sent_deltas: list[float] = []
    stance_deltas: list[float] = []
    topic_deltas: list[float] = []
    emb_deltas: list[float] = []
    split_passes: list[bool] = []

    total = len(states)
    for split_idx in range(n_splits):
        # Deterministic pseudo-resampling: circular shift then half split.
        offset = split_idx % total
        rotated = states[offset:] + states[:offset]
        half = total // 2
        batch_a = rotated[:half]
        batch_b = rotated[half:]
        if not batch_a or not batch_b:
            continue

        split_report = cross_batch_stability_report(batch_a=batch_a, batch_b=batch_b, tolerance=tolerance)
        sent_deltas.append(split_report.sentiment_mean_delta)
        stance_deltas.append(split_report.stance_mean_delta)
        topic_deltas.append(split_report.topic_l1_delta)
        emb_deltas.append(split_report.embedding_cosine_distance)
        split_passes.append(split_report.passed)

    if not sent_deltas:
        return StabilityReport(0.0, 0.0, 0.0, 0.0, 0, False)

    return StabilityReport(
        sentiment_mean_delta=float(sum(sent_deltas) / len(sent_deltas)),
        stance_mean_delta=float(sum(stance_deltas) / len(stance_deltas)),
        topic_l1_delta=float(sum(topic_deltas) / len(topic_deltas)),
        embedding_cosine_distance=float(sum(emb_deltas) / len(emb_deltas)),
        n_splits=len(sent_deltas),
        passed=all(split_passes),
    )


def report_to_dict(report: ContinuityReport | DecouplingReport | StabilityReport) -> dict[str, float | bool]:
    return asdict(report)
