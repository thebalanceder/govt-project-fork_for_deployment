"""Emotion expert with GoEmotions model + lexical fallback."""

from __future__ import annotations

from dataclasses import dataclass, field
import importlib
from typing import Any, Callable, cast

from .base import TaskExpertInput, TaskExpertOutput


def _safe_float(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


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
    model_id: str = "SamLowe/roberta-base-go_emotions"
    _classifier: Callable[[str], object] | None = field(init=False, default=None, repr=False)

    def _normalize_entries(self, raw: object) -> list[dict[str, object]]:
        if not isinstance(raw, list) or not raw:
            return []
        first = raw[0]
        if isinstance(first, list):
            source = first
        else:
            source = raw
        entries: list[dict[str, object]] = []
        for item in source:
            if isinstance(item, dict):
                entries.append(item)
        return entries

    def __post_init__(self) -> None:
        self._classifier = None
        try:
            transformers_mod = importlib.import_module("transformers")
            pipeline_factory = getattr(transformers_mod, "pipeline", None)
            if callable(pipeline_factory):
                candidate = pipeline_factory(
                    task="text-classification",
                    model=self.model_id,
                    return_all_scores=True,
                )
                if callable(candidate):
                    self._classifier = cast(Callable[[str], object], candidate)
        except Exception:
            self._classifier = None

    def _lexical_fallback(self, data: TaskExpertInput) -> TaskExpertOutput:
        text = data.merged_text().lower()
        counts: dict[str, int] = {}
        total = 0
        for emotion, tokens in EMOTION_LEXICON.items():
            hits = sum(token in text for token in tokens)
            counts[emotion] = hits
            total += hits

        if total == 0:
            distribution = {emotion: 0.0 for emotion in EMOTION_LEXICON}
            label = "neutral"
            score = 0.0
            confidence = 0.1
        else:
            distribution = {emotion: count / total for emotion, count in counts.items()}
            label = max(distribution, key=lambda key: distribution[key])
            confidence = distribution[label]
            score = distribution.get("joy", 0.0) - (
                distribution.get("anger", 0.0) + distribution.get("sadness", 0.0)
            )

        return TaskExpertOutput(
            name=self.name,
            label=label,
            score=float(score),
            confidence=float(confidence),
            payload={
                "backend": "lexical-fallback",
                "distribution": distribution,
                "target": data.target,
                "domain": data.domain,
            },
        )

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        text = data.merged_text()
        if self._classifier is None or not text:
            return self._lexical_fallback(data)

        raw = self._classifier(text)
        entries = self._normalize_entries(raw)
        if not entries:
            return self._lexical_fallback(data)

        distribution: dict[str, float] = {}
        for item in entries:
            label = str(item.get("label", "unknown")).lower()
            distribution[label] = _safe_float(item.get("score", 0.0))

        dominant = max(distribution, key=lambda key: distribution[key])
        confidence = distribution[dominant]
        score = distribution.get("joy", 0.0) - (
            distribution.get("anger", 0.0) + distribution.get("sadness", 0.0)
        )

        return TaskExpertOutput(
            name=self.name,
            label=dominant,
            score=float(max(-1.0, min(1.0, score))),
            confidence=float(confidence),
            payload={
                "backend": "hf-text-classification",
                "model": self.model_id,
                "distribution": distribution,
                "target": data.target,
                "domain": data.domain,
            },
        )
