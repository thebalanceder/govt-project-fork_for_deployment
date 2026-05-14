"""Pre-MiroFish expert research briefing agents (task-card / dashboard layer)."""

from .profiles import ResearchAgentProfile, all_research_profiles
from .researcher import (
    build_agent_prompt,
    build_evidence_text,
    research_run_result_from_dicts,
    run_all_research_agents,
    run_research_agent,
)
from .schema import ResearchReport, ResearchRunResult

__all__ = [
    "ResearchAgentProfile",
    "ResearchReport",
    "ResearchRunResult",
    "all_research_profiles",
    "build_agent_prompt",
    "build_evidence_text",
    "run_research_agent",
    "run_all_research_agents",
    "research_run_result_from_dicts",
]
