"""Risk / controversy expert."""

from __future__ import annotations

from dataclasses import dataclass

from .base import TaskExpertInput, TaskExpertOutput


RISK_TOKENS = {
    "risk",
    "danger",
    "unsafe",
    "uncertain",
    "volatile",
    "worry",
    "problem",
    "风险",
    "担心",
    "不稳定",
    "问题",
}

SAFE_TOKENS = {
    "stable",
    "reliable",
    "safe",
    "secure",
    "稳定",
    "可靠",
    "安全",
}


@dataclass(slots=True)
class RiskExpert:
    name: str = "risk"

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        text = " ".join([data.product_description, *data.comments]).lower()
        risk_hits = sum(token in text for token in RISK_TOKENS)
        safe_hits = sum(token in text for token in SAFE_TOKENS)
        total = risk_hits + safe_hits

        if total == 0:
            score = 0.5
            confidence = 0.2
            label = "MEDIUM_RISK"
        else:
            score = risk_hits / total
            confidence = min(1.0, total / 5.0)
            if score >= 0.6:
                label = "HIGH_RISK"
            elif score <= 0.4:
                label = "LOW_RISK"
            else:
                label = "MEDIUM_RISK"

        return TaskExpertOutput(
            name=self.name,
            label=label,
            score=float(score),
            confidence=float(confidence),
            payload={"risk_hits": risk_hits, "safe_hits": safe_hits},
        )
