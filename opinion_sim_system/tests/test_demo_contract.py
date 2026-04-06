from pathlib import Path

from ..demo.contracts import PHASE2B_SCHEMA_VERSION
from ..demo.run_demo import run_demo


def test_run_demo_emits_phase2b_contract(tmp_path: Path) -> None:
    payload = run_demo(output_dir=tmp_path)

    assert payload["schema_version"] == PHASE2B_SCHEMA_VERSION
    assert payload["demo"] == "phase2b"
    assert payload["generated_by"]["entrypoint"] == "run_demo"
    assert len(payload["cases"]) == 3

    sample = payload["cases"][0]
    assert set(sample.keys()) >= {"case", "input", "model_evidence", "simulation_result", "report", "report_text"}
    assert set(sample["input"].keys()) == {"text", "target", "domain"}
    assert set(sample["simulation_result"].keys()) >= {
        "initial_attitudes",
        "trajectories",
        "overall_final",
        "dispersion",
        "top_groups",
        "final_group_attitudes",
        "rounds",
        "visualization_payload",
    }
    assert set(sample["report"].keys()) >= {
        "schema_version",
        "status",
        "provider",
        "mode",
        "text",
        "executive_summary",
        "expanded_analysis",
        "decision_trace",
        "meta",
        "errors",
    }
    assert sample["report"]["schema_version"] == PHASE2B_SCHEMA_VERSION
    assert sample["report"]["text"] == sample["report_text"]
    assert sample["report"]["text"] == sample["report"]["expanded_analysis"]

    assert "visualization_payload" in sample["simulation_result"]

    artifact = Path(payload["artifact_path"])
    assert artifact.exists()
