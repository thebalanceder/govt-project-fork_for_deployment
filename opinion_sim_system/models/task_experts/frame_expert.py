"""Frame expert using sentence-frame classifier with fallback."""

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


FRAME_TOKENS: dict[str, set[str]] = {
    "economic": {"price", "cost", "value", "budget", "economy"},
    "health": {"health", "safe", "risk", "harm"},
    "fairness": {"fair", "equity", "justice", "equal"},
    "security": {"security", "protect", "threat", "defense"},
    "morality": {"ethical", "moral", "right", "wrong"},
}


@dataclass(slots=True)
class FrameExpert:
    name: str = "frame"
    model_id: str = "mattdr/sentence-frame-classifier"
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

    def _fallback(self, data: TaskExpertInput) -> TaskExpertOutput:
        text = data.merged_text().lower()
        counts: dict[str, float] = {}
        for frame, tokens in FRAME_TOKENS.items():
            counts[frame] = float(sum(token in text for token in tokens))

        total = float(sum(counts.values()))
        if total <= 0.0:
            distribution = {"general": 1.0}
            dominant = "general"
        else:
            distribution = {key: value / total for key, value in counts.items()}
            dominant = max(distribution, key=lambda key: distribution[key])

        return TaskExpertOutput(
            name=self.name,
            label=dominant,
            score=float(distribution[dominant]),
            confidence=float(distribution[dominant]),
            payload={
                "backend": "lexical-fallback",
                "distribution": distribution,
                "target": data.target,
                "domain": data.domain,
            },
        )

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        text = data.merged_text() or data.text
        if self._classifier is None or not text:
            return self._fallback(data)

        raw = self._classifier(text)
        entries = self._normalize_entries(raw)
        if not entries:
            return self._fallback(data)

        distribution: dict[str, float] = {}
        for item in entries:
            label = str(item.get("label", "unknown")).lower()
            distribution[label] = _safe_float(item.get("score", 0.0))

        dominant = max(distribution, key=lambda key: distribution[key])
        return TaskExpertOutput(
            name=self.name,
            label=dominant,
            score=float(distribution[dominant]),
            confidence=float(distribution[dominant]),
            payload={
                "backend": "hf-text-classification",
                "model": self.model_id,
                "distribution": distribution,
                "target": data.target,
                "domain": data.domain,
            },
        )
