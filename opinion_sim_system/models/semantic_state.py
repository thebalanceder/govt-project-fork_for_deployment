"""Unified semantic state contract for Semantic Frontend v2."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(slots=True)
class SemanticState:
    """Single semantic interface consumed by downstream dynamics.

    Required ranges:
    - sentiment in [-1, 1]
    - stance in [0, 1]
    - topic on simplex (sum to 1)
    - embedding in R^d (d > 0)
    """

    sentiment: float
    stance: float
    topic: dict[str, float]
    embedding: list[float]
    evidence_trace: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.sentiment = float(_clamp(float(self.sentiment), -1.0, 1.0))
        self.stance = float(_clamp(float(self.stance), 0.0, 1.0))

        if not self.embedding:
            msg = "embedding must be non-empty"
            raise ValueError(msg)
        self.embedding = [float(item) for item in self.embedding]

        if not self.topic:
            self.topic = {"topic_0": 1.0}

        cleaned: dict[str, float] = {}
        total = 0.0
        for key, value in self.topic.items():
            probability = max(0.0, float(value))
            cleaned[str(key)] = probability
            total += probability

        if total <= 0.0:
            cleaned = {"topic_0": 1.0}
            total = 1.0

        self.topic = {key: value / total for key, value in cleaned.items()}
        if not math.isclose(sum(self.topic.values()), 1.0, rel_tol=1e-7, abs_tol=1e-7):
            msg = "topic probabilities must sum to 1"
            raise ValueError(msg)
