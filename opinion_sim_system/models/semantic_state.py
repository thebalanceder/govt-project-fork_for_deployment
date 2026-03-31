"""Unified semantic state definition for phase1.1/1.2."""

from __future__ import annotations

from dataclasses import dataclass
import math


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(slots=True)
class SemanticState:
    """唯一语义状态接口。

    - sentiment ∈ [-1, 1]
    - stance ∈ [0, 1]
    - topic ∈ simplex (all probs >= 0 and sum ~= 1)
    - embedding ∈ R^d (d > 0)
    """

    sentiment: float
    stance: float
    topic: dict[str, float]
    embedding: list[float]

    def __post_init__(self) -> None:
        self.sentiment = float(_clamp(self.sentiment, -1.0, 1.0))
        self.stance = float(_clamp(self.stance, 0.0, 1.0))

        if not self.embedding:
            msg = "embedding must be non-empty"
            raise ValueError(msg)
        self.embedding = [float(item) for item in self.embedding]

        if not self.topic:
            self.topic = {"topic_0": 1.0}

        normalized_topic: dict[str, float] = {}
        total = 0.0
        for key, value in self.topic.items():
            p = max(0.0, float(value))
            normalized_topic[str(key)] = p
            total += p

        if total <= 0.0:
            normalized_topic = {"topic_0": 1.0}
            total = 1.0

        self.topic = {key: value / total for key, value in normalized_topic.items()}
        if not math.isclose(sum(self.topic.values()), 1.0, rel_tol=1e-7, abs_tol=1e-7):
            msg = "topic probabilities must sum to 1"
            raise ValueError(msg)
