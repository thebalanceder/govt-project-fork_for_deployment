"""Runtime switches for optional HuggingFace model loading."""

from __future__ import annotations

import os


TRUTHY_ENV = {"1", "true", "yes", "on"}


def hf_models_enabled() -> bool:
    return os.getenv("OPINION_SIM_ENABLE_HF_MODELS", "").strip().lower() in TRUTHY_ENV
