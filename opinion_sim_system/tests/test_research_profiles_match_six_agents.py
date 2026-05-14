from __future__ import annotations

from ..agents.six_agents import create_all_agents
from ..orchestrator.registry import agent_id_for_instance
from ..research_agents.profiles import all_research_profiles


def test_research_profiles_match_six_agents_identities() -> None:
    agents = create_all_agents()
    profiles = all_research_profiles()
    assert len(agents) == len(profiles) == 6
    by_id = {p.agent_id: p for p in profiles}
    for agent in agents:
        aid = agent_id_for_instance(agent)
        prof = by_id[aid]
        assert prof.display_name == agent.profile.name
        assert prof.title == agent.profile.title
