from pathlib import Path
import importlib

from ..simulation.runner import RunnerConfig

engine_mod = importlib.import_module("opinion_sim_system.simulation.engine")
AttitudeEngine = getattr(engine_mod, "AttitudeEngine")
run_attitude_engine = getattr(engine_mod, "run_attitude_engine")


def test_run_attitude_engine_returns_engine_contract(tmp_path: Path) -> None:
    output_file = tmp_path / "engine_output.json"
    result = run_attitude_engine(
        product_description="A reliable product with fair pricing.",
        comments=["great battery", "setup is confusing", "价格合理"],
        target="consumer electronics product",
        domain="product",
        config=RunnerConfig(rounds=3, seed=11),
        output_path=output_file,
    )

    assert output_file.exists()
    assert result["engine"]["name"] == "semantic_to_group_attitude_engine"
    assert result["engine"]["version"] == "phase2a"
    assert "semantic_evidence" in result


def test_attitude_engine_class_facade(tmp_path: Path) -> None:
    engine = AttitudeEngine(config=RunnerConfig(rounds=3, seed=13))
    output_file = tmp_path / "engine_class_output.json"
    result = engine.run(
        product_description="A support workflow with clear communication.",
        comments=["service is good", "response is slow", "沟通清楚"],
        target="support workflow",
        domain="support",
        output_path=output_file,
    )

    assert output_file.exists()
    assert "semantic_summary" in result
