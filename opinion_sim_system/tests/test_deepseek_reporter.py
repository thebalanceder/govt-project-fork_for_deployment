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
    assert isinstance(report["errors"], list)
    assert isinstance(report["text"], str)
    assert report["text"]


def test_reporter_generate_returns_text_alias() -> None:
    reporter = DeepSeekReporter(mode="fallback")
    text = reporter.generate(
        model_evidence={"experts": {}},
        simulation_result={"trajectories": []},
    )
    assert isinstance(text, str)
    assert text
