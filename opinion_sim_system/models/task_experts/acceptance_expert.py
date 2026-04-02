"""Target-conditioned acceptance expert (BART-MNLI style zero-shot + fallback)."""

from __future__ import annotations

from dataclasses import dataclass, field
import importlib
from typing import Any, Callable, cast

from .base import TaskExpertInput, TaskExpertOutput


SUPPORT_TOKENS = {"support", "agree", "approve", "favorable", "like", "accept", "支持", "认可"}
CAUTIOUS_TOKENS = {"cautious", "uncertain", "mixed", "hesitant", "担心", "观望", "谨慎"}
REJECT_TOKENS = {"reject", "oppose", "against", "disagree", "hate", "反对", "拒绝", "不满"}


@dataclass(slots=True)
class AcceptanceExpert:
    name: str = "acceptance"
    model_id: str = "facebook/bart-large-mnli"
    _classifier: Callable[..., dict[str, Any]] | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self._classifier = None
        try:
            transformers_mod = importlib.import_module("transformers")
            pipeline_factory = getattr(transformers_mod, "pipeline", None)
            if callable(pipeline_factory):
                candidate = pipeline_factory(task="zero-shot-classification", model=self.model_id)
                if callable(candidate):
                    self._classifier = cast(Callable[..., dict[str, Any]], candidate)
        except Exception:
            self._classifier = None

    def _fallback(self, data: TaskExpertInput) -> TaskExpertOutput:
        text = data.merged_text().lower()
        support_hits = sum(token in text for token in SUPPORT_TOKENS)
        cautious_hits = sum(token in text for token in CAUTIOUS_TOKENS)
        reject_hits = sum(token in text for token in REJECT_TOKENS)
        total = support_hits + cautious_hits + reject_hits

        if total == 0:
            label = "IS CAUTIOUS ABOUT THIS TARGET"
            score = 0.5
            confidence = 0.2
        else:
            support_score = support_hits / total
            cautious_score = cautious_hits / total
            reject_score = reject_hits / total
            if support_score >= cautious_score and support_score >= reject_score:
                label = "ACCEPTS THIS TARGET"
                score = 1.0
                confidence = support_score
            elif reject_score >= cautious_score:
                label = "REJECTS THIS TARGET"
                score = 0.0
                confidence = reject_score
            else:
                label = "IS CAUTIOUS ABOUT THIS TARGET"
                score = 0.5
                confidence = cautious_score

        return TaskExpertOutput(
            name=self.name,
            label=label,
            score=float(score),
            confidence=float(confidence),
            payload={
                "backend": "lexical-fallback",
                "target": data.target,
                "domain": data.domain,
            },
        )

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        labels = [
            "accepts this target",
            "is cautious about this target",
            "rejects this target",
        ]
        text = data.merged_text() or data.text
        if self._classifier is None or not text:
            return self._fallback(data)

        hypothesis_template = f"In the {data.domain} domain and target '{data.target}', this text is {{}}."
        raw = self._classifier(
            text,
            candidate_labels=labels,
            hypothesis_template=hypothesis_template,
            multi_label=False,
        )

        ordered_labels = [str(item).upper() for item in raw.get("labels", [])]
        ordered_scores = [float(item) for item in raw.get("scores", [])]
        if not ordered_labels or not ordered_scores:
            return self._fallback(data)

        top_label = ordered_labels[0]
        top_score = ordered_scores[0]
        if "ACCEPTS" in top_label:
            scalar = 1.0
        elif "REJECTS" in top_label:
            scalar = 0.0
        else:
            scalar = 0.5

        return TaskExpertOutput(
            name=self.name,
            label=top_label,
            score=scalar,
            confidence=float(top_score),
            payload={
                "backend": "hf-zero-shot",
                "model": self.model_id,
                "labels": ordered_labels,
                "scores": ordered_scores,
                "target": data.target,
                "domain": data.domain,
                "hypothesis_template": hypothesis_template,
            },
        )
