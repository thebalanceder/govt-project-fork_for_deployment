"""Attitude update rule implementation for Phase 1."""

from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(slots=True)
class UpdateConfig:
    inertia: float = 0.6
    alpha: float = 0.25
    beta: float = 0.15
    noise_std: float = 0.02
    clamp_min: float = 0.0
    clamp_max: float = 1.0

    def __post_init__(self) -> None:
        if self.inertia < 0 or self.alpha < 0 or self.beta < 0:
            msg = "inertia, alpha, beta must be non-negative"
            raise ValueError(msg)
        if self.clamp_min >= self.clamp_max:
            msg = "clamp_min must be less than clamp_max"
            raise ValueError(msg)


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
