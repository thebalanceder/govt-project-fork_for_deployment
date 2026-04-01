"""Shared interfaces and dataclasses for task experts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class TaskExpertInput:
    product_description: str
    comments: list[str]


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
