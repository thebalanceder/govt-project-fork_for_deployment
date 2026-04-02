"""Phase2B one-click demo: semantic evidence -> simulation -> structured report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import PHASE2B_SCHEMA_VERSION
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
    base = Path(output_dir) if output_dir else Path(__file__).resolve().parents[1] / "artifacts" / "phase2b_demo"
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
        model_evidence = result.get("semantic_evidence", {})
        report = reporter.generate_report(model_evidence=model_evidence, simulation_result=result)
        report_text = str(report.get("text", ""))

        final_round = result["trajectories"][-1]
        cases_output.append(
            {
                "case": case["name"],
                "input": {
                    "text": case["text"],
                    "target": case["target"],
                    "domain": case["domain"],
                },
                "model_evidence": model_evidence,
                "simulation_result": {
                    "overall_final": final_round["overall_satisfaction"],
                    "final_group_attitudes": final_round["group_attitudes"],
                    "rounds": len(result["trajectories"]),
                },
                "report": report,
                "report_text": report_text,
            }
        )

    payload = {
        "schema_version": PHASE2B_SCHEMA_VERSION,
        "demo": "phase2b",
        "generated_by": {"entrypoint": "run_demo", "engine": "run_attitude_engine"},
        "cases": cases_output,
    }
    out_file = base / "demo_output.json"
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    payload["artifact_path"] = str(out_file)
    return payload


def run_one_click_demo(output_dir: str | Path | None = None) -> dict[str, Any]:
    """Alias for product-facing one-click invocation."""
    return run_demo(output_dir=output_dir)


if __name__ == "__main__":
    result = run_demo()
    print(json.dumps({"artifact_path": result["artifact_path"], "n_cases": len(result["cases"])}, ensure_ascii=False))
