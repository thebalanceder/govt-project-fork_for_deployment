"""Sentiment expert wrapper."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..sentiment.sentiment_model import SentimentModel
from .base import TaskExpertInput, TaskExpertOutput


@dataclass(slots=True)
class SentimentExpert:
    name: str = "sentiment"
    backend: str = "auto"
    _model: SentimentModel = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._model = SentimentModel(backend=self.backend)

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        samples = [*data.comments]
        if not samples and data.product_description:
            samples = [data.product_description]

        results = self._model.analyze(samples)
        if not results:
            return TaskExpertOutput(name=self.name, label="NEUTRAL", score=0.0, confidence=0.0)

        mean_score = float(sum(item.score for item in results) / len(results))
        if mean_score > 0.1:
            label = "POSITIVE"
        elif mean_score < -0.1:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"

        confidence = min(1.0, abs(mean_score))
        return TaskExpertOutput(
            name=self.name,
            label=label,
            score=mean_score,
            confidence=confidence,
            payload={"n_samples": len(results), "backend": self._model.backend},
        )
