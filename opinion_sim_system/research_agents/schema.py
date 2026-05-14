"""Structured types for research briefing outputs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ResearchReport:
    agent_id: str
    display_name: str
    title: str
    research_focus: str
    status: str
    report_text: str
    errors: list[str] = field(default_factory=list)


@dataclass
class ResearchRunResult:
    run_id: str
    reports: list[ResearchReport]
    errors: list[str] = field(default_factory=list)
