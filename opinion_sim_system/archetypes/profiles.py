"""Hand-crafted six-dimensional archetype profiles for Phase 1."""

from __future__ import annotations

from copy import deepcopy


DIMENSIONS = ["efficiency", "cost", "culture", "emotion", "conformity", "risk"]

SIX_ARCHETYPE_PROFILES: dict[str, dict[str, float]] = {
    "rational_evaluator": {
        "efficiency": 0.95,
        "cost": 0.65,
        "culture": 0.20,
        "emotion": 0.20,
        "conformity": 0.35,
        "risk": 0.55,
    },
    "budget_guardian": {
        "efficiency": 0.50,
        "cost": 0.95,
        "culture": 0.15,
        "emotion": 0.25,
        "conformity": 0.45,
        "risk": 0.65,
    },
    "culture_seeker": {
        "efficiency": 0.35,
        "cost": 0.40,
        "culture": 0.95,
        "emotion": 0.55,
        "conformity": 0.40,
        "risk": 0.40,
    },
    "emotional_resonator": {
        "efficiency": 0.25,
        "cost": 0.30,
        "culture": 0.55,
        "emotion": 0.95,
        "conformity": 0.50,
        "risk": 0.45,
    },
    "social_follower": {
        "efficiency": 0.40,
        "cost": 0.45,
        "culture": 0.50,
        "emotion": 0.60,
        "conformity": 0.95,
        "risk": 0.50,
    },
    "risk_averse": {
        "efficiency": 0.65,
        "cost": 0.65,
        "culture": 0.25,
        "emotion": 0.35,
        "conformity": 0.40,
        "risk": 0.95,
    },
}


def get_default_profiles() -> dict[str, dict[str, float]]:
    """Return independent copies of six archetype profiles."""
    return deepcopy(SIX_ARCHETYPE_PROFILES)


def derive_initial_attitudes(sentiment_signal: float) -> dict[str, float]:
    """Map semantic sentiment signal [-1, 1] to six-group initial attitudes [0, 1]."""
    base = (sentiment_signal + 1.0) / 2.0
    profiles = get_default_profiles()
    attitudes: dict[str, float] = {}
    for group, weights in profiles.items():
        sensitivity = 0.5 * weights["efficiency"] + 0.3 * weights["emotion"] + 0.2 * weights["risk"]
        value = 0.5 + (base - 0.5) * (0.8 + 0.4 * sensitivity)
        attitudes[group] = max(0.0, min(1.0, value))
    return attitudes
