from __future__ import annotations

from ..research_agents.profiles import all_research_profiles
from ..research_agents.researcher import run_research_agent


def test_research_agent_fallback_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    prof = all_research_profiles()[0]
    row = run_research_agent(
        prof,
        {"case_id": "x", "data": {}},
        "short evidence",
        deepseek_mode="auto",
    )
    assert row["status"] == "fallback"
    assert row["errors"] == []
    assert "## 1. Key judgment" in row["report_text"]
    assert prof.display_name in row["display_name"]


def test_run_all_profiles_fallback(monkeypatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    from ..research_agents.researcher import run_all_research_agents

    rows = run_all_research_agents({"data": {}}, "evidence", deepseek_mode="auto", run_id="r1")
    assert len(rows) == 6
    assert all(r["status"] == "fallback" for r in rows)
