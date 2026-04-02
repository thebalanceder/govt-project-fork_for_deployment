"""Sentiment expert wrapper using HF model with fallback."""

from __future__ import annotations

from dataclasses import dataclass, field
import importlib
from typing import Any, Callable, cast

from ..sentiment.sentiment_model import SentimentModel
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


@dataclass(slots=True)
class SentimentExpert:
    name: str = "sentiment"
    backend: str = "auto"
    model_id: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    _model: SentimentModel = field(init=False, repr=False)
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
        self._model = SentimentModel(backend=self.backend)
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

    def _map_label(self, raw_label: str) -> tuple[str, float]:
        label = raw_label.upper()
        if "NEG" in label or label.endswith("0"):
            return "NEGATIVE", -1.0
        if "POS" in label or label.endswith("2"):
            return "POSITIVE", 1.0
        return "NEUTRAL", 0.0

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        samples = [*data.comments]
        if not samples and data.text:
            samples = [data.text]

        if self._classifier is not None and samples:
            merged = " ".join(samples)
            raw = self._classifier(merged)
            entries = self._normalize_entries(raw)
            if entries:
                top_label = "NEUTRAL"
                top_score = 0.0
                signed = 0.0
                for item in entries:
                    mapped_label, sign = self._map_label(str(item.get("label", "")))
                    score = _safe_float(item.get("score", 0.0))
                    if score > top_score:
                        top_score = score
                        top_label = mapped_label
                        signed = sign * score
                return TaskExpertOutput(
                    name=self.name,
                    label=top_label,
                    score=float(max(-1.0, min(1.0, signed))),
                    confidence=float(top_score),
                    payload={
                        "n_samples": len(samples),
                        "backend": "hf-text-classification",
                        "model": self.model_id,
                        "target": data.target,
                        "domain": data.domain,
                    },
                )

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
            payload={
                "n_samples": len(results),
                "backend": self._model.backend,
                "target": data.target,
                "domain": data.domain,
            },
        )
