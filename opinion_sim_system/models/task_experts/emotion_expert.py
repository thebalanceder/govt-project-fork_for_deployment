"""Emotion expert with lightweight lexical scoring."""

from __future__ import annotations

from dataclasses import dataclass

from .base import TaskExpertInput, TaskExpertOutput


EMOTION_LEXICON: dict[str, set[str]] = {
    "joy": {"great", "excellent", "happy", "love", "满意", "喜欢", "高兴"},
    "anger": {"angry", "furious", "annoyed", "糟糕", "愤怒", "不满"},
    "fear": {"risk", "danger", "worry", "担心", "害怕", "风险"},
    "sadness": {"sad", "disappointed", "失望", "难过"},
    "surprise": {"surprising", "unexpected", "惊讶", "意外"},
}


@dataclass(slots=True)
class EmotionExpert:
    name: str = "emotion"

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        text = " ".join([data.product_description, *data.comments]).lower()
        counts: dict[str, int] = {}
        total = 0
        for emotion, tokens in EMOTION_LEXICON.items():
            hits = sum(token in text for token in tokens)
            counts[emotion] = hits
            total += hits

        if total == 0:
            return TaskExpertOutput(
                name=self.name,
                label="neutral",
                score=0.0,
                confidence=0.1,
                payload={"distribution": {emotion: 0.0 for emotion in EMOTION_LEXICON}},
            )

        distribution = {emotion: count / total for emotion, count in counts.items()}
        dominant = max(distribution, key=lambda key: distribution[key])
        confidence = distribution[dominant]
        # Score maps positive affect vs negative affect.
        score = distribution.get("joy", 0.0) - (distribution.get("anger", 0.0) + distribution.get("sadness", 0.0))

        return TaskExpertOutput(
            name=self.name,
            label=dominant,
            score=float(score),
            confidence=float(confidence),
            payload={"distribution": distribution},
        )
