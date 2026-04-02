"""Shared interfaces and dataclasses for task experts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class InputCase:
    """Target-conditioned input case for semantic front-end experts."""

    text: str
    target: str
    domain: str


@dataclass(slots=True)
class TaskExpertInput(InputCase):
    comments: list[str] = field(default_factory=list)

    @classmethod
    def from_legacy(
        cls,
        product_description: str,
        comments: list[str],
        target: str | None = None,
        domain: str = "product",
    ) -> TaskExpertInput:
        text = str(product_description) if product_description is not None else ""
        normalized_comments = [str(item) if item is not None else "" for item in comments]
        case_target = str(target) if target is not None else text
        return cls(text=text, target=case_target, domain=domain, comments=normalized_comments)

    @property
    def product_description(self) -> str:
        """Backward-compatible alias for previous field naming."""
        return self.text

    def merged_text(self) -> str:
        return " ".join([self.text, *self.comments]).strip()


@dataclass(slots=True)
class TaskExpertOutput:
    name: str
    label: str
    score: float
    confidence: float
    payload: dict[str, Any] = field(default_factory=dict)


class TaskExpert(Protocol):
    name: str

    def analyze(self, data: TaskExpertInput) -> TaskExpertOutput:
        """Produce structured expert output."""
        ...
