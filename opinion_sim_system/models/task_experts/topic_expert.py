"""Topic expert wrapper built on TopicModel."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..topic.topic_model import TopicModel
from .base import TaskExpertInput, TaskExpertOutput


@dataclass(slots=True)
class TopicExpert:
    name: str = "topic"
    backend: str = "auto"
    _model: TopicModel = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._model = TopicModel(backend=self.backend)

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        docs = [*data.comments]
        if not docs and data.text:
            docs = [data.text]
        if not docs and data.target:
            docs = [data.target]

        topics, topic_words = self._model.fit_transform(docs)
        if not topics:
            return TaskExpertOutput(
                name=self.name,
                label="topic_0",
                score=1.0,
                confidence=0.0,
                payload={
                    "distribution": {"topic_0": 1.0},
                    "topic_words": topic_words,
                    "backend": self._model.backend,
                    "target": data.target,
                    "domain": data.domain,
                },
            )

        counts: dict[str, int] = {}
        confidence_sum = 0.0
        for item in topics:
            label = f"topic_{item.topic_id}"
            counts[label] = counts.get(label, 0) + 1
            confidence_sum += float(item.probability)

        total = sum(counts.values())
        distribution = {label: count / total for label, count in sorted(counts.items())}
        dominant = max(distribution, key=lambda key: distribution[key])

        return TaskExpertOutput(
            name=self.name,
            label=dominant,
            score=float(distribution[dominant]),
            confidence=float(confidence_sum / max(len(topics), 1)),
            payload={
                "distribution": distribution,
                "topic_words": topic_words,
                "backend": self._model.backend,
                "target": data.target,
                "domain": data.domain,
            },
        )
