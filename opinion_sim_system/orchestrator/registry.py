"""Stable agent_id mapping for domain experts (must match six_agents display names)."""

from __future__ import annotations

from typing import Any

from ..agents.six_agents import create_all_agents

_CLASS_TO_AGENT_ID: dict[str, str] = {
    "EconomistAgent": "economist_agent",
    "PolicyAgent": "policy_agent",
    "BusinessAgent": "business_agent",
    "SociologistAgent": "sociologist_agent",
    "IRAgent": "ir_agent",
    "PublicAgent": "public_agent",
}


def agent_id_for_instance(agent: object) -> str:
    name = agent.__class__.__name__
    if name not in _CLASS_TO_AGENT_ID:
        raise KeyError(f"Unknown agent class for registry: {name}")
    return _CLASS_TO_AGENT_ID[name]


def get_domain_expert_entries() -> list[dict[str, Any]]:
    """Runtime registry from six_agents (single source of truth for display names)."""
    rows: list[dict[str, Any]] = []
    for agent in create_all_agents():
        rows.append(
            {
                "agent_id": agent_id_for_instance(agent),
                "display_name": agent.profile.name,
                "title": agent.profile.title,
                "python_class": agent.__class__.__name__,
                "expertise_topics": list(agent.profile.expertise_topics),
            }
        )
    return rows


def display_name_by_agent_id() -> dict[str, str]:
    return {row["agent_id"]: row["display_name"] for row in get_domain_expert_entries()}
