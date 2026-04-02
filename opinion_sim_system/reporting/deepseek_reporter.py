"""DeepSeek reporting placeholder for Phase2A demos.

This module intentionally does not call any external API in-repo.
It provides a deterministic text summary interface so downstream callers
can later swap in real DeepSeek integration without changing call sites.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DeepSeekReporter:
    provider: str = "deepseek"
    mode: str = "placeholder"

    def generate(self, model_evidence: dict[str, Any], simulation_result: dict[str, Any]) -> str:
        experts = model_evidence.get("experts", {}) if isinstance(model_evidence, dict) else {}
        acceptance = experts.get("acceptance", {}) if isinstance(experts, dict) else {}
        conflict = experts.get("conflict", {}) if isinstance(experts, dict) else {}
        frame = experts.get("frame", {}) if isinstance(experts, dict) else {}

        trajectories = simulation_result.get("trajectories", []) if isinstance(simulation_result, dict) else []
        final_overall = trajectories[-1].get("overall_satisfaction", 0.0) if trajectories else 0.0

        return (
            "[DeepSeek placeholder] "
            f"acceptance={acceptance.get('label', 'N/A')}, "
            f"conflict={conflict.get('label', 'N/A')}, "
            f"frame={frame.get('label', 'N/A')}, "
            f"final_overall={float(final_overall):.3f}."
        )
