"""Research-agent personas aligned with six_agents.py (display names must match exactly)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResearchAgentProfile:
    agent_id: str
    display_name: str
    title: str
    research_focus: str
    prompt_role: str


def all_research_profiles() -> tuple[ResearchAgentProfile, ...]:
    return (
        ResearchAgentProfile(
            agent_id="economist_agent",
            display_name="Dr. Lim Wei Chen",
            title="Chief Economist",
            research_focus=(
                "macroeconomic impact, inflation, employment, fiscal pressure, market confidence"
            ),
            prompt_role=(
                "Chief Economist (Dr. Lim Wei Chen) preparing an internal macroeconomic briefing "
                "for the chief coordinator"
            ),
        ),
        ResearchAgentProfile(
            agent_id="policy_agent",
            display_name="Datin Sri Aisha binti Abdullah",
            title="Policy Advisor",
            research_focus=(
                "governance, policy feasibility, implementation risk, public welfare"
            ),
            prompt_role=(
                "Policy Advisor (Datin Sri Aisha binti Abdullah) preparing a governance and "
                "implementation-risk briefing for the chief coordinator"
            ),
        ),
        ResearchAgentProfile(
            agent_id="business_agent",
            display_name="Encik Razak bin Ibrahim",
            title="Business Leader",
            research_focus=(
                "industry response, investment climate, business confidence, competitiveness"
            ),
            prompt_role=(
                "Business Leader (Encik Razak bin Ibrahim) preparing an industry and investment "
                "climate briefing for the chief coordinator"
            ),
        ),
        ResearchAgentProfile(
            agent_id="sociologist_agent",
            display_name="Dr. Muthu a/l Krishnan",
            title="Sociologist",
            research_focus=(
                "social cohesion, inequality, identity, public trust, cultural sensitivity"
            ),
            prompt_role=(
                "Sociologist (Dr. Muthu a/l Krishnan) preparing a social cohesion and trust briefing "
                "for the chief coordinator"
            ),
        ),
        ResearchAgentProfile(
            agent_id="ir_agent",
            display_name="Ms. Wong Li Ming",
            title="International Relations Expert",
            research_focus=(
                "ASEAN context, geopolitical implications, trade relations, diplomatic risk"
            ),
            prompt_role=(
                "International relations expert (Ms. Wong Li Ming) preparing a regional and "
                "diplomatic-risk briefing for the chief coordinator"
            ),
        ),
        ResearchAgentProfile(
            agent_id="public_agent",
            display_name="Ahmad bin Hassan",
            title="Public Representative",
            research_focus=(
                "citizen concerns, cost of living, service quality, public acceptance"
            ),
            prompt_role=(
                "Public representative (Ahmad bin Hassan) preparing a citizen-impact and "
                "acceptance briefing for the chief coordinator"
            ),
        ),
    )
