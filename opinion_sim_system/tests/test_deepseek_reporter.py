from ..demo.contracts import PHASE2B_SCHEMA_VERSION
from ..reporting.deepseek_reporter import DeepSeekReporter


def test_reporter_fallback_envelope_without_api_key() -> None:
    reporter = DeepSeekReporter(mode="auto", api_key="")
    model_evidence = {
        "experts": {
            "acceptance": {"label": "ACCEPT"},
            "conflict": {"label": "LOW_CONFLICT"},
            "frame": {"label": "fairness"},
        }
    }
    simulation_result = {"trajectories": [{"overall_satisfaction": 0.77}]}

    report = reporter.generate_report(model_evidence=model_evidence, simulation_result=simulation_result)
    assert report["schema_version"] == PHASE2B_SCHEMA_VERSION
    assert report["provider"] == "deepseek"
    assert report["mode"] == "fallback"
    assert report["status"] == "ok"
    assert isinstance(report["executive_summary"], dict)
    assert isinstance(report["expanded_analysis"], str)
    assert isinstance(report["decision_trace"], dict)
    assert isinstance(report["errors"], list)
    assert isinstance(report["text"], str)
    assert report["text"]
    assert report["text"] == report["expanded_analysis"]
    assert "conclusion_line" in report["executive_summary"]
    assert "overall_final" in report["decision_trace"]


def test_reporter_generate_returns_text_alias() -> None:
    reporter = DeepSeekReporter(mode="fallback")
    text = reporter.generate(
        model_evidence={"experts": {}},
        simulation_result={"trajectories": []},
    )
    assert isinstance(text, str)
    assert text


def test_expand_orchestrator_briefing_skips_without_api_key() -> None:
    reporter = DeepSeekReporter(mode="auto", api_key="")
    out = reporter.expand_orchestrator_briefing("# Title\n\nBody")
    assert out["status"] == "skipped"
    assert out["text"] == ""
    assert out["errors"] == []


def test_reporter_executive_summary_contains_core_slots() -> None:
    reporter = DeepSeekReporter(mode="fallback")
    report = reporter.generate_report(
        model_evidence={
            "experts": {
                "acceptance": {"label": "ACCEPT", "score": 0.81},
                "conflict": {"label": "LOW_CONFLICT", "score": 0.22},
                "frame": {"label": "fairness", "score": 0.66},
            }
        },
        simulation_result={
            "trajectories": [
                {"overall_satisfaction": 0.55, "group_attitudes": {"a": 0.61, "b": 0.41}},
                {"overall_satisfaction": 0.62, "group_attitudes": {"a": 0.64, "b": 0.43}},
            ]
        },
    )

    summary = report["executive_summary"]
    assert isinstance(summary["conclusion_line"], str)
    assert isinstance(summary["headline"], str)
    assert set(summary["four_block_summary"].keys()) == {
        "acceptance_outlook",
        "polarization",
        "main_driver",
        "recommended_action",
    }
