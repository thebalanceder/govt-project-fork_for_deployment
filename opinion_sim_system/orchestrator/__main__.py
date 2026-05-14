"""CLI: python -m opinion_sim_system.orchestrator --case <path.json>"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .runner import run_orchestrated_case


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Dr. Helena Marlowe (chief briefing coordinator) orchestration + MiroFish tracks.",
    )
    parser.add_argument(
        "--case",
        type=Path,
        required=True,
        help="JSON file with case payload (must include 'data' dict for MiroFish).",
    )
    parser.add_argument("--rounds", type=int, default=3, help="MiroFish discussion rounds per topic.")
    parser.add_argument("--verbose", action="store_true", help="Print engine stdout + stderr summary path.")
    parser.add_argument(
        "--deepseek",
        choices=["auto", "off", "live"],
        default="auto",
        help="DeepSeek optional briefing expansion (never required for core run).",
    )
    args = parser.parse_args()
    if not args.case.is_file():
        print(f"Case file not found: {args.case}", file=sys.stderr)
        sys.exit(1)
    case = json.loads(args.case.read_text(encoding="utf-8"))
    result = run_orchestrated_case(
        case,
        num_rounds=args.rounds,
        verbose=args.verbose,
        deepseek_mode=args.deepseek,
    )
    print(json.dumps({"run_id": result["run_id"], "artifacts_dir": result["artifacts_dir"]}, indent=2))


if __name__ == "__main__":
    main()
