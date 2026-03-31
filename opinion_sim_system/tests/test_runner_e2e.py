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
        config=RunnerConfig(rounds=3, seed=123, enforce_semantic_guarantees=False),
        output_path=output_file,
    )

    assert output_file.exists()
    assert len(result["initial_attitudes"]) == 6
    assert len(result["trajectories"]) >= 3

    persisted = json.loads(output_file.read_text(encoding="utf-8"))
    assert "initial_attitudes" in persisted
    assert "trajectories" in persisted
    assert "semantic_state" in persisted
    assert "semantic_experiments" in persisted
    assert "stage3_calibration" in persisted
    assert "task_generalization" in persisted
    assert "three_loop_consistency" in persisted
    assert "dynamics_metrics" in persisted
    assert len(persisted["initial_attitudes"]) == 6
    assert len(persisted["trajectories"]) >= 3

    first_round = persisted["trajectories"][0]
    assert set(first_round.keys()) == {
        "round",
        "group_attitudes",
        "overall_satisfaction",
        "topic_distribution",
        "attribution",
    }
    assert len(first_round["group_attitudes"]) == 6
    assert len(first_round["attribution"]) == 6
    sample_group = next(iter(first_round["attribution"].values()))
    assert set(sample_group.keys()) == {
        "self",
        "semantic",
        "neighbor",
        "noise",
        "self_contribution",
        "semantic_contribution",
        "neighbor_contribution",
        "noise_contribution",
    }

    assert set(persisted["semantic_state"].keys()) == {"sentiment", "stance", "topic", "embedding"}
    assert set(persisted["semantic_experiments"].keys()) == {
        "continuity",
        "decoupling",
        "cross_batch_stability",
    }
    assert persisted["semantic_experiments"]["cross_batch_stability"]["n_splits"] >= 1
    assert "perturbation_distances" in persisted["stage3_calibration"]
    assert "scenario_volatility" in persisted["stage3_calibration"]
    assert "response_vectors" in persisted["task_generalization"]
    assert "pairwise_vector_distance" in persisted["task_generalization"]
    assert len(persisted["task_generalization"]["response_vectors"]) == 3
    assert set(persisted["task_generalization"]["tasks"].keys()) == {"policy", "product", "support"}
    assert persisted["api_frontend_bundle"]["api_version"] == "phase1.3"
    assert "dispersion" in persisted["dynamics_metrics"]
    assert set(persisted["three_loop_consistency"].keys()) == {
        "semantic_closure",
        "dynamics_closure",
        "decision_closure",
    }


def test_runner_requires_input() -> None:
    with unittest.TestCase().assertRaisesRegex(ValueError, "product_description or comments"):
        run_phase1_simulation(product_description="", comments=[])


def test_runner_description_only_uses_sample_comments(tmp_path: Path) -> None:
    output_file = tmp_path / "phase1_output_from_description_only.json"

    result = run_phase1_simulation(
        product_description="A practical and reliable product with balanced value.",
        comments=None,
        config=RunnerConfig(rounds=3, seed=9, enforce_semantic_guarantees=False),
        output_path=output_file,
    )

    assert output_file.exists()
    assert len(result["initial_attitudes"]) == 6
    assert len(result["trajectories"]) >= 3
    assert "api_frontend_bundle" in result
