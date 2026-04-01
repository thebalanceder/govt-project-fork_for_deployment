from pathlib import Path
import json
import unittest

from ..simulation.runner import RunnerConfig, run_phase1_simulation


def test_runner_outputs_m1_artifact_with_three_rounds(tmp_path: Path) -> None:
    output_file = tmp_path / "phase1_output.json"

    result = run_phase1_simulation(
        product_description="A reliable product with strong battery and fair pricing.",
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
    assert len(persisted["initial_attitudes"]) == 6
    assert len(persisted["trajectories"]) >= 3

    first_round = persisted["trajectories"][0]
    assert set(first_round.keys()) == {
        "round",
        "group_attitudes",
        "overall_satisfaction",
        "topic_distribution",
    }
    assert len(first_round["group_attitudes"]) == 6
    assert "semantic_summary" in persisted
    assert persisted["semantic_summary"]["mapper_version"] == "v2"
    assert "stance_signal" in persisted["semantic_summary"]
    assert "semantic_trace" in persisted["semantic_summary"]


def test_runner_requires_input() -> None:
    with unittest.TestCase().assertRaisesRegex(ValueError, "product_description or comments"):
        run_phase1_simulation(product_description="", comments=[])


def test_runner_description_only_uses_sample_comments(tmp_path: Path) -> None:
    output_file = tmp_path / "phase1_output_from_description_only.json"

    result = run_phase1_simulation(
        product_description="A practical and reliable product with balanced value.",
        comments=None,
        config=RunnerConfig(rounds=3, seed=9),
        output_path=output_file,
    )

    assert output_file.exists()
    assert len(result["initial_attitudes"]) == 6
    assert len(result["trajectories"]) >= 3
