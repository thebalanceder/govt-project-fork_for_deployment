"""Conflict/toxicity expert with HF offensive baseline + fallback."""

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


CONFLICT_TOKENS = {
    "offensive",
    "toxic",
    "abuse",
    "hate",
    "attack",
    "conflict",
    "冲突",
    "攻击",
    "辱骂",
    "仇恨",
}

CALM_TOKENS = {
    "constructive",
    "calm",
    "civil",
    "respectful",
    "理性",
    "冷静",
    "尊重",
}


@dataclass(slots=True)
class ConflictExpert:
    name: str = "conflict"
    model_id: str = "cardiffnlp/twitter-roberta-base-offensive"
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
        conflict_hits = sum(token in text for token in CONFLICT_TOKENS)
        calm_hits = sum(token in text for token in CALM_TOKENS)
        total = conflict_hits + calm_hits
        if total == 0:
            score = 0.5
            confidence = 0.2
            label = "MEDIUM_CONFLICT"
        else:
            score = conflict_hits / total
            confidence = min(1.0, total / 5.0)
            if score >= 0.6:
                label = "HIGH_CONFLICT"
            elif score <= 0.4:
                label = "LOW_CONFLICT"
            else:
                label = "MEDIUM_CONFLICT"

        return TaskExpertOutput(
            name=self.name,
            label=label,
            score=float(score),
            confidence=float(confidence),
            payload={
                "backend": "lexical-fallback",
                "conflict_hits": conflict_hits,
                "calm_hits": calm_hits,
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

        top_label = ""
        top_score = 0.0
        offensive_score = 0.0
        for item in entries:
            label = str(item.get("label", "")).upper()
            score = _safe_float(item.get("score", 0.0))
            if score > top_score:
                top_score = score
                top_label = label
            if "OFF" in label or "LABEL_1" in label:
                offensive_score = score

        conflict_score = max(0.0, min(1.0, offensive_score))
        if conflict_score >= 0.6:
            mapped_label = "HIGH_CONFLICT"
        elif conflict_score <= 0.4:
            mapped_label = "LOW_CONFLICT"
        else:
            mapped_label = "MEDIUM_CONFLICT"

        return TaskExpertOutput(
            name=self.name,
            label=mapped_label,
            score=float(conflict_score),
            confidence=float(top_score),
            payload={
                "backend": "hf-text-classification",
                "model": self.model_id,
                "raw_top_label": top_label,
                "target": data.target,
                "domain": data.domain,
            },
        )
