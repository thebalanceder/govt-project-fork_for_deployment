"""Chief briefing coordinator persona (orchestration layer only; not a BaseAgent)."""

from __future__ import annotations

from dataclasses import dataclass

CHIEF_AGENT_ID = "chief_briefing_coordinator"
CHIEF_DISPLAY_NAME = "Dr. Helena Marlowe"
CHIEF_TITLE = "Chief Briefing Coordinator"
CHIEF_BACKGROUND = (
    "A senior evidence-to-decision coordinator responsible for decomposing a case into expert tasks, "
    "assigning work to domain Dr. agents, tracking progress, resolving conflicts, and producing "
    "the final decision brief."
)


@dataclass(frozen=True)
class ChiefCoordinatorProfile:
    agent_id: str
    display_name: str
    title: str
    background: str


CHIEF_PROFILE = ChiefCoordinatorProfile(
    agent_id=CHIEF_AGENT_ID,
    display_name=CHIEF_DISPLAY_NAME,
    title=CHIEF_TITLE,
    background=CHIEF_BACKGROUND,
)
