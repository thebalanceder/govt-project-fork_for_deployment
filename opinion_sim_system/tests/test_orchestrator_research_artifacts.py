from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from ..agents.base_agent import AgentState
from ..mirofish.discussion import DiscussionResult, DiscussionRound
from ..orchestrator.runner import run_orchestrated_case

_DISPLAY_NAMES = [
    "Dr. Lim Wei Chen",
    "Datin Sri Aisha binti Abdullah",
    "Encik Razak bin Ibrahim",
    "Dr. Muthu a/l Krishnan",
    "Ms. Wong Li Ming",
    "Ahmad bin Hassan",
]


def _fake_discussion_result(topic: str) -> DiscussionResult:
    now = datetime.now()
    st = AgentState(
        topic=topic,
        sentiment=0.05,
        confidence=0.7,
        key_factors=[],
        reasoning="stub",
        forecast_7d=0.05,
        forecast_30d=0.05,
        timestamp=now,
    )
    states = {name: st for name in _DISPLAY_NAMES}
    r0 = DiscussionRound(
        round_number=0,
        agent_states=states,
        responses=[],
        average_sentiment=0.05,
        convergence_score=0.5,
        timestamp=now,
    )
    forecasts = {
        name: {"sentiment": 0.05, "forecast_7d": 0.05, "forecast_30d": 0.05, "confidence": 0.7}
        for name in _DISPLAY_NAMES
    }
    return DiscussionResult(
        topic=topic,
        rounds=[r0],
        final_consensus=0.05,
        convergence_rate=0.5,
        agent_forecasts=forecasts,
        explanation="stub integration",
        timestamp=now,
    )


def test_orchestrator_writes_research_artifacts_and_timeline(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    def _fake_run_discussion(self, data, topic, num_rounds=3):
        return _fake_discussion_result(topic)

    case = {
        "run_id": "pytest_orchestrator_research",
        "text": "Integration smoke",
        "topics": ["economic"],
        "data": {"economic": [], "political": [], "cultural": [], "social_media": [], "news": []},
    }

    with patch(
        "opinion_sim_system.orchestrator.runner.MiroFishDiscussion.run_discussion",
        new=_fake_run_discussion,
    ):
        out = run_orchestrated_case(case, num_rounds=1, verbose=False, output_base=tmp_path)

    d = Path(out["artifacts_dir"])
    assert (d / "research_reports.json").is_file()
    assert (d / "research_reports.md").is_file()
    assert (d / "orchestration_trace.json").is_file()
    assert (d / "agent_timeline.json").is_file()
    assert (d / "briefing_report.md").is_file()
    assert (d / "briefing_report.html").is_file()

    trace = json.loads((d / "orchestration_trace.json").read_text(encoding="utf-8"))
    assert "research_reports" in trace
    assert len(trace["research_reports"]["reports"]) == 6

    timeline = json.loads((d / "agent_timeline.json").read_text(encoding="utf-8"))
    for aid in [
        "economist_agent",
        "policy_agent",
        "business_agent",
        "sociologist_agent",
        "ir_agent",
        "public_agent",
    ]:
        evs = [e for e in timeline["events"] if e.get("agent_id") == aid]
        phases = {e["phase"] for e in evs}
        assert "research_assigned" in phases
        assert "research_working" in phases
        assert phases.intersection({"research_completed", "research_failed"})

    md = (d / "briefing_report.md").read_text(encoding="utf-8")
    assert "## Expert Research Briefs" in md
    assert "## Consensus" in md
    assert "Dr. Lim Wei Chen" in md

    assert "artifacts" in out
    assert "research_reports_json" in out["artifacts"]
