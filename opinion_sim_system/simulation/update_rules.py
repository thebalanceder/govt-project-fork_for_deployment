"""Attitude update rule implementation for Phase 1."""

from __future__ import annotations

from dataclasses import dataclass
import random

from ..models.semantic_state import SemanticState


@dataclass(slots=True)
class UpdateConfig:
    inertia: float = 0.6
    alpha: float = 0.25
    beta: float = 0.15
    noise_std: float = 0.02
    clamp_min: float = 0.0
    clamp_max: float = 1.0
    max_step_delta: float = 0.2

    def __post_init__(self) -> None:
        if self.inertia < 0 or self.alpha < 0 or self.beta < 0:
            msg = "inertia, alpha, beta must be non-negative"
            raise ValueError(msg)
        if self.clamp_min >= self.clamp_max:
            msg = "clamp_min must be less than clamp_max"
            raise ValueError(msg)
        if self.max_step_delta <= 0:
            msg = "max_step_delta must be positive"
            raise ValueError(msg)


def _bounded_step(target_state: float, current_state: float, max_delta: float) -> float:
    delta = target_state - current_state
    if delta > max_delta:
        return current_state + max_delta
    if delta < -max_delta:
        return current_state - max_delta
    return target_state


def _semantic_target(semantic_state: SemanticState, agent_profile: dict[str, float]) -> float:
    emotion_sensitivity = float(agent_profile.get("emotion", 0.5))
    risk_aversion = float(agent_profile.get("risk", 0.5))
    conformity = float(agent_profile.get("conformity", 0.5))

    sentiment_01 = (semantic_state.sentiment + 1.0) / 2.0
    base = 0.55 * semantic_state.stance + 0.45 * sentiment_01

    adjustment = (
        0.10 * (emotion_sensitivity - 0.5) * (sentiment_01 - 0.5)
        - 0.08 * (risk_aversion - 0.5)
    )
    adjusted = base + adjustment
    if conformity > 0.8:
        adjusted = 0.90 * adjusted + 0.10 * semantic_state.stance
    return max(0.0, min(1.0, adjusted))


def heterogeneous_update_attitude(
    agent_profile: dict[str, float],
    agent_state: float,
    neighbors_state: float,
    semantic_state: SemanticState,
    config: UpdateConfig,
    rng: random.Random,
) -> tuple[float, dict[str, float]]:
    """Phase1.2 heterogeneous update.

    f(agent_profile, agent_state, neighbors_state, semantic_state)
    with bounded-step guard to prevent divergence.
    """

    semantic_target = _semantic_target(semantic_state, agent_profile)
    conformity = float(agent_profile.get("conformity", 0.5))

    self_contrib = config.inertia * agent_state
    semantic_contrib = config.alpha * semantic_target
    neighbor_contrib = config.beta * (0.5 + 0.5 * conformity) * neighbors_state
    noise = rng.gauss(0.0, config.noise_std) if config.noise_std > 0 else 0.0

    proposed = self_contrib + semantic_contrib + neighbor_contrib + noise
    bounded = _bounded_step(proposed, current_state=agent_state, max_delta=config.max_step_delta)
    next_state = max(config.clamp_min, min(config.clamp_max, bounded))

    attribution = {
        # phase1.3 canonical categories
        "self": self_contrib,
        "semantic": semantic_contrib,
        "neighbor": neighbor_contrib,
        "noise": noise,
        # compatibility aliases
        "self_contribution": self_contrib,
        "semantic_contribution": semantic_contrib,
        "neighbor_contribution": neighbor_contrib,
        "noise_contribution": noise,
    }
    return next_state, attribution


def update_attitude(
    current_state: float,
    input_state: float,
    mean_neighbor_state: float,
    config: UpdateConfig,
    rng: random.Random,
) -> float:
    """Apply Phase 1 update equation with configurable coefficients.

    next = inertia*self + alpha*input_state + beta*neighbor_mean + noise
    """
    noise = rng.gauss(0.0, config.noise_std) if config.noise_std > 0 else 0.0
    next_state = (
        config.inertia * current_state
        + config.alpha * input_state
        + config.beta * mean_neighbor_state
        + noise
    )
    return max(config.clamp_min, min(config.clamp_max, next_state))
