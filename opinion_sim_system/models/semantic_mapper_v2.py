"""Semantic Frontend v2 mapper with six task experts + evidence trace."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .embedding.embedder import Embedder
from .semantic_fusion import fuse_semantic_state
from .semantic_state import SemanticState
from .task_experts import (
    AcceptanceExpert,
    ConflictExpert,
    EmotionExpert,
    FrameExpert,
    InputCase,
    SentimentExpert,
    TaskExpertInput,
    TopicExpert,
)
from .task_experts.base import TaskExpertOutput


def cosine_distance(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.asarray(vec_a, dtype=np.float64)
    b = np.asarray(vec_b, dtype=np.float64)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if math.isclose(denom, 0.0, abs_tol=1e-12):
        return 0.0
    cosine = float(np.dot(a, b) / denom)
    cosine = max(-1.0, min(1.0, cosine))
    return 1.0 - cosine


@dataclass(slots=True)
class SemanticMapperV2:
    embedder: Embedder
    sentiment_expert: SentimentExpert
    acceptance_expert: AcceptanceExpert
    emotion_expert: EmotionExpert
    topic_expert: TopicExpert
    conflict_expert: ConflictExpert
    frame_expert: FrameExpert

    @classmethod
    def with_defaults(cls) -> SemanticMapperV2:
        return cls(
            embedder=Embedder(),
            sentiment_expert=SentimentExpert(),
            acceptance_expert=AcceptanceExpert(),
            emotion_expert=EmotionExpert(),
            topic_expert=TopicExpert(),
            conflict_expert=ConflictExpert(),
            frame_expert=FrameExpert(),
        )

    def _pool_embedding(self, description: str, comments: list[str]) -> list[float]:
        matrix = self.embedder.encode([description, *comments])
        if matrix.size == 0:
            msg = "empty embedding matrix"
            raise ValueError(msg)
        pooled = np.asarray(matrix, dtype=np.float64).mean(axis=0)
        norm = float(np.linalg.norm(pooled))
        if norm > 0:
            pooled = pooled / norm
        return [float(item) for item in pooled.tolist()]

    def _collect_expert_outputs(self, data: TaskExpertInput) -> dict[str, TaskExpertOutput]:
        return {
            "sentiment": self.sentiment_expert.analyze(data),
            "acceptance": self.acceptance_expert.analyze(data),
            "emotion": self.emotion_expert.analyze(data),
            "topic": self.topic_expert.analyze(data),
            "conflict": self.conflict_expert.analyze(data),
            "frame": self.frame_expert.analyze(data),
        }

    def build(self, product_description: str, comments: list[str], target: str | None = None, domain: str = "product") -> SemanticState:
        description = str(product_description) if product_description is not None else ""
        normalized_comments = [str(item) if item is not None else "" for item in comments]
        if not description.strip() and not normalized_comments:
            msg = "product_description or comments must be provided"
            raise ValueError(msg)

        data = TaskExpertInput.from_legacy(
            product_description=description,
            comments=normalized_comments,
            target=target,
            domain=domain,
        )
        expert_outputs = self._collect_expert_outputs(data)
        pooled_embedding = self._pool_embedding(description=description, comments=normalized_comments)
        return fuse_semantic_state(expert_outputs=expert_outputs, embedding=pooled_embedding)

    def build_from_case(self, case: InputCase, comments: list[str] | None = None) -> SemanticState:
        normalized_comments = [str(item) if item is not None else "" for item in (comments or [])]
        data = TaskExpertInput(
            text=str(case.text),
            target=str(case.target),
            domain=str(case.domain),
            comments=normalized_comments,
        )
        expert_outputs = self._collect_expert_outputs(data)
        pooled_embedding = self._pool_embedding(description=data.text, comments=data.comments)
        return fuse_semantic_state(expert_outputs=expert_outputs, embedding=pooled_embedding)
