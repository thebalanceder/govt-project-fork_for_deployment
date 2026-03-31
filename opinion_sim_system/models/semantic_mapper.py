"""Map model outputs into a single SemanticState."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .embedding.embedder import Embedder
from .semantic_state import SemanticState
from .sentiment.sentiment_model import SentimentModel
from .topic.topic_model import TopicModel


def _topic_distribution(topic_ids: list[int]) -> dict[str, float]:
    if not topic_ids:
        return {"topic_0": 1.0}
    counts: dict[int, int] = {}
    for topic_id in topic_ids:
        counts[int(topic_id)] = counts.get(int(topic_id), 0) + 1
    total = sum(counts.values())
    return {f"topic_{topic_id}": count / total for topic_id, count in sorted(counts.items())}


def _mean_sentiment(scores: list[float]) -> float:
    if not scores:
        return 0.0
    return max(-1.0, min(1.0, float(sum(scores) / len(scores))))


def _topic_certainty(topic: dict[str, float]) -> float:
    if not topic:
        return 0.0
    best = max(topic.values())
    topic_size = max(len(topic), 1)
    floor = 1.0 / topic_size
    if best <= floor:
        return 0.0
    return (best - floor) / (1.0 - floor) if floor < 1.0 else 1.0


def _to_stance(sentiment: float, topic: dict[str, float]) -> float:
    sentiment_part = (sentiment + 1.0) / 2.0
    certainty_part = _topic_certainty(topic)
    # Decoupled blend: sentiment is primary, topic confidence is secondary.
    return max(0.0, min(1.0, 0.75 * sentiment_part + 0.25 * certainty_part))


@dataclass(slots=True)
class SemanticMapper:
    """Construct SemanticState from raw texts through existing semantic modules."""

    embedder: Embedder
    sentiment_model: SentimentModel
    topic_model: TopicModel

    @classmethod
    def with_defaults(cls) -> SemanticMapper:
        return cls(
            embedder=Embedder(),
            sentiment_model=SentimentModel(),
            topic_model=TopicModel(),
        )

    def build(self, product_description: str, comments: list[str]) -> SemanticState:
        description = str(product_description) if product_description is not None else ""
        normalized_comments = [str(item) if item is not None else "" for item in comments]
        corpus = [description, *normalized_comments]

        embeddings = self.embedder.encode(corpus)
        if embeddings.size == 0:
            msg = "empty embedding matrix"
            raise ValueError(msg)

        sentiment_scores = [item.score for item in self.sentiment_model.analyze(normalized_comments)]
        sentiment = _mean_sentiment(sentiment_scores)

        topics, _ = self.topic_model.fit_transform(normalized_comments)
        topic_ids = [item.topic_id for item in topics]
        topic_distribution = _topic_distribution(topic_ids)

        pooled = np.asarray(embeddings, dtype=np.float64).mean(axis=0)
        norm = float(np.linalg.norm(pooled))
        if norm > 0:
            pooled = pooled / norm
        embedding_vector = [float(item) for item in pooled.tolist()]

        stance = _to_stance(sentiment=sentiment, topic=topic_distribution)
        return SemanticState(
            sentiment=sentiment,
            stance=stance,
            topic=topic_distribution,
            embedding=embedding_vector,
        )

    def build_for_single_text(self, text: str) -> SemanticState:
        """Build a state for continuity/decoupling experiments."""
        content = str(text) if text is not None else ""
        return self.build(product_description=content, comments=[content])


def cosine_distance(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.asarray(vec_a, dtype=np.float64)
    b = np.asarray(vec_b, dtype=np.float64)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if math.isclose(denom, 0.0, abs_tol=1e-12):
        return 0.0
    cosine = float(np.dot(a, b) / denom)
    cosine = max(-1.0, min(1.0, cosine))
    return 1.0 - cosine
