"""Demo entrypoints for Phase2B.

Keep imports lazy to avoid circular import chains during package init.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

__all__ = ["run_demo", "run_one_click_demo"]


def run_demo(output_dir: str | Path | None = None) -> dict[str, Any]:
    from .run_demo import run_demo as _run_demo

    return _run_demo(output_dir=output_dir)


def run_one_click_demo(output_dir: str | Path | None = None) -> dict[str, Any]:
    from .run_demo import run_one_click_demo as _run_one_click_demo

    return _run_one_click_demo(output_dir=output_dir)
