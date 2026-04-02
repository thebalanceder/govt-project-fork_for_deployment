"""Stance expert using support/oppose lexical cues."""

from __future__ import annotations

from dataclasses import dataclass

from .base import TaskExpertInput, TaskExpertOutput


SUPPORT_TOKENS = {"support", "agree", "approve", "favorable", "支持", "赞同", "认可"}
OPPOSE_TOKENS = {"oppose", "reject", "disagree", "against", "反对", "质疑", "不满"}


@dataclass(slots=True)
class StanceExpert:
    name: str = "stance"

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        text = " ".join([data.product_description, *data.comments]).lower()

        support_hits = sum(token in text for token in SUPPORT_TOKENS)
        oppose_hits = sum(token in text for token in OPPOSE_TOKENS)
        total = support_hits + oppose_hits

        if total == 0:
            score = 0.5
            label = "MIXED"
            confidence = 0.2
        else:
            signed = (support_hits - oppose_hits) / total
            score = (signed + 1.0) / 2.0
            if score > 0.6:
                label = "SUPPORT"
            elif score < 0.4:
                label = "OPPOSE"
            else:
                label = "MIXED"
            confidence = min(1.0, total / 4.0)

        return TaskExpertOutput(
            name=self.name,
            label=label,
            score=float(score),
            confidence=float(confidence),
            payload={"support_hits": support_hits, "oppose_hits": oppose_hits},
        )
