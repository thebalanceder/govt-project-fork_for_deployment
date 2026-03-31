from pathlib import Path

from ..simulation.engine import AttitudeEngine, run_attitude_engine
from ..simulation.runner import RunnerConfig


def test_engine_function_entrypoint_returns_phase13_contract(tmp_path: Path) -> None:
    output_file = tmp_path / "engine_output.json"
    result = run_attitude_engine(
        product_description="A product with reliable performance and balanced price.",
        comments=["battery is stable", "setup is confusing", "price is good"],
        config=RunnerConfig(rounds=3, seed=17, enforce_semantic_guarantees=False),
        output_path=output_file,
    )

    assert output_file.exists()
    assert result["engine"]["name"] == "semantic_to_group_attitude_engine"
    assert result["engine"]["version"] == "phase1.3"
    assert result["api_frontend_bundle"]["api_version"] == "phase1.3"


def test_engine_class_facade_works(tmp_path: Path) -> None:
    engine = AttitudeEngine(config=RunnerConfig(rounds=3, seed=21, enforce_semantic_guarantees=False))
    output_file = tmp_path / "engine_class_output.json"
    result = engine.run(
        product_description="A support workflow with transparent communication.",
        comments=["support is clear", "response time is slow", "态度很好"],
        output_path=output_file,
    )

    assert output_file.exists()
    assert "three_loop_consistency" in result
    assert "semantic_experiments" in result
