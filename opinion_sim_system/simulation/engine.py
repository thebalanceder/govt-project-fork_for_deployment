"""Phase1.3 attitude engine facade.

Provides a stable integration interface for downstream API/frontend packaging.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .runner import RunnerConfig, run_phase1_simulation


@dataclass(slots=True)
class AttitudeEngine:
    """Thin facade over runner, exposing a phase1.3 engine contract."""

    config: RunnerConfig

    def run(
        self,
        product_description: str,
        comments: list[str] | None = None,
        output_path: str | Path | None = None,
    ) -> dict[str, Any]:
        result = run_phase1_simulation(
            product_description=product_description,
            comments=comments,
            config=self.config,
            output_path=output_path,
        )
        result["engine"] = {
            "name": "semantic_to_group_attitude_engine",
            "version": "phase1.3",
        }
        return result


def run_attitude_engine(
    product_description: str,
    comments: list[str] | None = None,
    config: RunnerConfig | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Public function entrypoint for phase1.3 engine execution."""

    runtime = config or RunnerConfig()
    engine = AttitudeEngine(config=runtime)
    return engine.run(
        product_description=product_description,
        comments=comments,
        output_path=output_path,
    )
