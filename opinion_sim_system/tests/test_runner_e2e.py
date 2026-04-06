from pathlib import Path
import json
import unittest

from ..models.semantic_state import SemanticState
from ..simulation import runner as runner_module
from ..simulation.runner import RunnerConfig, run_phase1_simulation


def test_runner_outputs_m1_artifact_with_three_rounds(tmp_path: Path) -> None:
    output_file = tmp_path / "phase1_output.json"

    result = run_phase1_simulation(
        product_description="A reliable product with strong battery and fair pricing.",
        target="battery-powered device",
        domain="product",
        comments=[
            "great value and stable performance",
            "价格合理，体验不错",
            "setup is confusing",
        ],
        config=RunnerConfig(rounds=3, seed=123),
        output_path=output_file,
    )

    assert output_file.exists()
    assert len(result["initial_attitudes"]) == 6
    assert len(result["trajectories"]) >= 3

    persisted = json.loads(output_file.read_text(encoding="utf-8"))
    assert "initial_attitudes" in persisted
    assert "trajectories" in persisted
    assert "semantic_state" in persisted
    assert "semantic_trace" in persisted
    assert "semantic_evidence" in persisted
    assert len(persisted["initial_attitudes"]) == 6
    assert len(persisted["trajectories"]) >= 3

    first_round = persisted["trajectories"][0]
    assert {
        "round",
        "group_attitudes",
        "overall_satisfaction",
        "topic_distribution",
    }.issubset(first_round.keys())
    assert {
        "delta_by_group",
        "overall_delta",
        "dominant_driver",
        "dispersion",
        "activation_reasons",
    }.issubset(first_round.keys())
    assert len(first_round["group_attitudes"]) == 6

    assert "visualization_payload" in persisted
    payload = persisted["visualization_payload"]
    assert payload["schema_version"] == "phase3.v1"
    assert payload["round_count"] == len(persisted["trajectories"])
    assert len(payload["rounds"]) == len(persisted["trajectories"])
    assert "divergence_summary" in payload
    assert "driver_summary" in payload
    assert "semantic_summary" in persisted
    assert persisted["semantic_summary"]["mapper_version"] == "v2"
    assert "stance_signal" in persisted["semantic_summary"]
    assert "semantic_trace" in persisted["semantic_summary"]
    assert "semantic_evidence" in persisted["semantic_summary"]
    assert persisted["input"]["target"] == "battery-powered device"
    assert persisted["input"]["domain"] == "product"

    experts = persisted["semantic_evidence"]["experts"]
    assert "acceptance" in experts
    assert "conflict" in experts
    assert "frame" in experts


def test_runner_requires_input() -> None:
    with unittest.TestCase().assertRaisesRegex(ValueError, "product_description or comments"):
        run_phase1_simulation(product_description="", comments=[])


def test_runner_description_only_uses_sample_comments(tmp_path: Path) -> None:
    output_file = tmp_path / "phase1_output_from_description_only.json"

    result = run_phase1_simulation(
        product_description="A practical and reliable product with balanced value.",
        target="practical product",
        domain="product",
        comments=None,
        config=RunnerConfig(rounds=3, seed=9),
        output_path=output_file,
    )

    assert output_file.exists()
    assert len(result["initial_attitudes"]) == 6
    assert len(result["trajectories"]) >= 3


def test_runner_uses_input_case_build_path(tmp_path: Path) -> None:
    output_file = tmp_path / "phase1_output_input_case_path.json"
    captured: dict[str, str] = {}
    original = runner_module.SemanticMapperV2.build_from_case

    def _fake_build_from_case(self: object, case: object, comments: list[str] | None = None) -> SemanticState:
        case_obj = case
        captured["text"] = str(getattr(case_obj, "text", ""))
        captured["target"] = str(getattr(case_obj, "target", ""))
        captured["domain"] = str(getattr(case_obj, "domain", ""))
        return SemanticState(
            sentiment=0.1,
            stance=0.6,
            topic={"topic_0": 0.7, "topic_1": 0.3},
            embedding=[0.2, -0.1, 0.3, 0.4],
            evidence_trace={"experts": {}},
        )

    runner_module.SemanticMapperV2.build_from_case = _fake_build_from_case
    try:
        _ = run_phase1_simulation(
            product_description="A clear product message.",
            target="battery-powered device",
            domain="product",
            comments=["good battery", "setup is okay", "price is fair"],
            config=RunnerConfig(rounds=3, seed=5),
            output_path=output_file,
        )
    finally:
        runner_module.SemanticMapperV2.build_from_case = original

    assert captured["text"] == "A clear product message."
    assert captured["target"] == "battery-powered device"
    assert captured["domain"] == "product"
