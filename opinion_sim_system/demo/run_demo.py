"""Minimal Phase2A demo: six-task semantic frontend -> engine -> report payload."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..reporting.deepseek_reporter import DeepSeekReporter
from ..simulation.engine import run_attitude_engine
from ..simulation.runner import RunnerConfig


def _demo_cases() -> list[dict[str, Any]]:
    return [
        {
            "name": "policy_case",
            "text": "The policy is fair but implementation is too slow for citizens.",
            "target": "public policy",
            "domain": "policy",
            "comments": [
                "transparent and fair process",
                "response speed is still slow",
                "communication feels clearer now",
            ],
        },
        {
            "name": "product_case",
            "text": "The product battery is excellent but setup remains confusing.",
            "target": "smart home product",
            "domain": "product",
            "comments": [
                "great battery life and stable performance",
                "setup is confusing",
                "good value for price",
            ],
        },
        {
            "name": "culture_case",
            "text": "The cultural trend is innovative but may increase social conflict.",
            "target": "cultural trend",
            "domain": "culture",
            "comments": [
                "creative and inspiring movement",
                "might divide communities",
                "discussion quality is improving",
            ],
        },
    ]


def run_demo(output_dir: str | Path | None = None) -> dict[str, Any]:
    base = Path(output_dir) if output_dir else Path(__file__).resolve().parents[1] / "artifacts" / "phase2a_demo"
    base.mkdir(parents=True, exist_ok=True)

    reporter = DeepSeekReporter()
    cases_output: list[dict[str, Any]] = []

    for index, case in enumerate(_demo_cases()):
        result = run_attitude_engine(
            product_description=case["text"],
            target=case["target"],
            domain=case["domain"],
            comments=case["comments"],
            config=RunnerConfig(rounds=3, seed=42 + index),
            output_path=base / f"{case['name']}_engine.json",
        )
        report_text = reporter.generate(model_evidence=result.get("semantic_evidence", {}), simulation_result=result)
        cases_output.append(
            {
                "case": case["name"],
                "model_evidence": result.get("semantic_evidence", {}),
                "simulation_result": {
                    "overall_final": result["trajectories"][-1]["overall_satisfaction"],
                    "final_group_attitudes": result["trajectories"][-1]["group_attitudes"],
                    "rounds": len(result["trajectories"]),
                },
                "report_text": report_text,
            }
        )

    payload = {"demo": "phase2a", "cases": cases_output}
    out_file = base / "demo_output.json"
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    payload["artifact_path"] = str(out_file)
    return payload


if __name__ == "__main__":
    result = run_demo()
    print(json.dumps({"artifact_path": result["artifact_path"], "n_cases": len(result["cases"])}, ensure_ascii=False))
