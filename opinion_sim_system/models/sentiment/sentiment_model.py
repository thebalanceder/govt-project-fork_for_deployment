"""Sentiment analysis adapter for Phase 1.

Supports HuggingFace pipeline when available, with an offline lexicon fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from typing import Callable, Iterable, cast


POSITIVE_TOKENS = {
    "great",
    "excellent",
    "smooth",
    "stable",
    "recommend",
    "good",
    "love",
    "喜欢",
    "满意",
    "实用",
    "稳定",
    "不错",
}

NEGATIVE_TOKENS = {
    "bad",
    "slow",
    "confusing",
    "lag",
    "laggy",
    "poor",
    "disappointed",
    "卡顿",
    "失望",
    "慢",
    "问题",
}


@dataclass(slots=True)
class SentimentResult:
    label: str
    score: float


def _safe_float(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _token_score(text: str) -> float:
    normalized = text.lower()
    pos_hits = sum(token in normalized for token in POSITIVE_TOKENS)
    neg_hits = sum(token in normalized for token in NEGATIVE_TOKENS)
    total = pos_hits + neg_hits
    if total == 0:
        return 0.0
    return (pos_hits - neg_hits) / total


class SentimentModel:
    """Sentiment adapter with optional transformers backend."""

    def __init__(self, backend: str = "auto") -> None:
        self.backend = backend
        self._pipeline: Callable[[list[str]], list[dict[str, object]]] | None = None

        if backend in {"auto", "transformers"}:
            try:
                transformers_mod = importlib.import_module("transformers")
                pipeline_factory = getattr(transformers_mod, "pipeline", None)
                if not callable(pipeline_factory):
                    raise RuntimeError("transformers.pipeline is not callable")

                pipeline_obj = pipeline_factory("sentiment-analysis")
                if not callable(pipeline_obj):
                    raise RuntimeError("sentiment pipeline object is not callable")
                self._pipeline = cast(Callable[[list[str]], list[dict[str, object]]], pipeline_obj)
                self.backend = "transformers"
            except Exception:
                self._pipeline = None
                self.backend = "lexicon"
        else:
            self.backend = "lexicon"

    def analyze(self, texts: Iterable[str]) -> list[SentimentResult]:
        text_list = [str(item) if item is not None else "" for item in texts]
        if self._pipeline is not None:
            raw = self._pipeline(text_list)
            results: list[SentimentResult] = []
            for item in raw:
                label = str(item["label"]).upper()
                if "NEG" in label:
                    mapped = "NEGATIVE"
                    signed_score = -_safe_float(item["score"])
                elif "POS" in label:
                    mapped = "POSITIVE"
                    signed_score = _safe_float(item["score"])
                else:
                    mapped = "NEUTRAL"
                    signed_score = 0.0
                results.append(SentimentResult(label=mapped, score=signed_score))
            return results

        fallback: list[SentimentResult] = []
        for text in text_list:
            score = _token_score(text)
            if score > 0.1:
                label = "POSITIVE"
            elif score < -0.1:
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"
            fallback.append(SentimentResult(label=label, score=score))
        return fallback
