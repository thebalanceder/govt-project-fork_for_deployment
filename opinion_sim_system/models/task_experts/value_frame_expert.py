"""Value-frame expert mapping text to six archetype dimensions."""

from __future__ import annotations

from dataclasses import dataclass

from ...archetypes.profiles import DIMENSIONS
from .base import TaskExpertInput, TaskExpertOutput


VALUE_TOKENS: dict[str, set[str]] = {
    "efficiency": {"fast", "efficient", "performance", "快速", "效率", "性能"},
    "cost": {"cheap", "price", "value", "budget", "价格", "成本", "性价比"},
    "culture": {"identity", "community", "culture", "文化", "传统", "认同"},
    "emotion": {"feel", "trust", "emotion", "满意", "喜欢", "情感"},
    "conformity": {"trend", "everyone", "social", "主流", "跟随", "社交"},
    "risk": {"risk", "safe", "uncertain", "风险", "安全", "不确定"},
}


@dataclass(slots=True)
class ValueFrameExpert:
    name: str = "value_frame"

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        text = " ".join([data.product_description, *data.comments]).lower()
        counts: dict[str, float] = {dimension: 0.0 for dimension in DIMENSIONS}

        for dimension, tokens in VALUE_TOKENS.items():
            counts[dimension] = float(sum(token in text for token in tokens))

        total = float(sum(counts.values()))
        if total <= 0:
            distribution = {dimension: 1.0 / len(DIMENSIONS) for dimension in DIMENSIONS}
        else:
            distribution = {dimension: value / total for dimension, value in counts.items()}

        dominant = max(distribution, key=lambda key: distribution[key])
        return TaskExpertOutput(
            name=self.name,
            label=dominant,
            score=float(distribution[dominant]),
            confidence=float(distribution[dominant]),
            payload={"distribution": distribution},
        )
