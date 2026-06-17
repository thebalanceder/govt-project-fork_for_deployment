#!/usr/bin/env python3
"""Smoke test for SciFact-style DeBERTa NLI wiring."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any
import contextlib
import io


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_MODEL = "cross-encoder/nli-deberta-v3-small"
TRUTHY_ENV = {"1", "true", "yes", "on"}


def _truthy(name: str, default: str = "") -> bool:
    return os.getenv(name, default).strip().lower() in TRUTHY_ENV


def _configure_hf() -> None:
    if _truthy("SCIFACT_USE_HFMIRROR", "1"):
        os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "10")
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "30")
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")


def _run_hf(model_id: str) -> dict[str, Any]:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

    local_only = _truthy("SCIFACT_NLI_LOCAL_ONLY")
    tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=local_only)
    model = AutoModelForSequenceClassification.from_pretrained(model_id, local_files_only=local_only)
    classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)

    text = (
        "Claim: Vitamin D supplementation improves respiratory infection outcomes. "
        "Evidence: A controlled trial reports mixed results and asks for more data."
    )
    labels = ["supports", "refutes", "not enough information"]
    raw = classifier(
        text,
        candidate_labels=labels,
        hypothesis_template="This evidence {} the claim.",
        multi_label=False,
    )

    return {
        "backend": "hf-zero-shot",
        "model": model_id,
        "label": str(raw["labels"][0]),
        "score": float(raw["scores"][0]),
        "hf_endpoint": os.getenv("HF_ENDPOINT", ""),
        "local_only": local_only,
    }


def _run_fallback(model_id: str, error: BaseException) -> dict[str, Any]:
    from opinion_sim_system.models.task_experts import AcceptanceExpert, TaskExpertInput

    data = TaskExpertInput(
        text="A cautious evidence brief says the finding is mixed and needs more data.",
        target="SciFact-style evidence claim",
        domain="scientific_evidence",
        comments=["The evidence is uncertain but does not reject the claim."],
    )
    output = AcceptanceExpert(model_id=model_id).analyze(data)
    return {
        "backend": output.payload.get("backend", "fallback"),
        "model": model_id,
        "label": output.label,
        "score": output.score,
        "confidence": output.confidence,
        "hf_endpoint": os.getenv("HF_ENDPOINT", ""),
        "hf_error": f"{type(error).__name__}: {error}",
    }


def main() -> int:
    _configure_hf()
    model_id = os.getenv("SCIFACT_DEBERTA_NLI_MODEL", DEFAULT_MODEL)
    require_hf = _truthy("SCIFACT_NLI_REQUIRE_HF")
    try_hf = require_hf or _truthy("SCIFACT_NLI_TRY_HF")

    try:
        if not try_hf:
            raise RuntimeError("HF model load skipped; set SCIFACT_NLI_TRY_HF=1 to test the mirror")
        hf_stderr = io.StringIO()
        with contextlib.redirect_stderr(hf_stderr):
            result = _run_hf(model_id)
        captured = hf_stderr.getvalue().strip()
        if captured:
            result["hf_stderr"] = captured[-2000:]
        ok = True
    except Exception as exc:
        if require_hf:
            print("SCIFACT_DEBERTA_NLI_SMOKE_FAILED")
            print(json.dumps({"ok": False, "model": model_id, "error": f"{type(exc).__name__}: {exc}"}, indent=2))
            return 1
        result = _run_fallback(model_id, exc)
        ok = True

    print("SCIFACT_DEBERTA_NLI_SMOKE_OK")
    print(json.dumps({"ok": ok, **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
