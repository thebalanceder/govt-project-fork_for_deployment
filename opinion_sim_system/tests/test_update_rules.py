import random
import unittest

from ..models.semantic_state import SemanticState
from ..simulation.update_rules import UpdateConfig, heterogeneous_update_attitude, update_attitude


def test_update_rule_without_noise_is_deterministic() -> None:
    cfg = UpdateConfig(inertia=0.6, alpha=0.25, beta=0.15, noise_std=0.0)
    rng = random.Random(7)

    state = update_attitude(0.8, 0.7, 0.6, cfg, rng)
    # Expected: 0.6*0.8 + 0.25*0.7 + 0.15*0.6 = 0.48 + 0.175 + 0.09 = 0.745
    assert abs(state - 0.745) < 1e-9


def test_invalid_update_config_raises() -> None:
    with unittest.TestCase().assertRaisesRegex(ValueError, "non-negative"):
        UpdateConfig(inertia=-0.1)


def test_heterogeneous_update_returns_bounded_state_and_attribution() -> None:
    cfg = UpdateConfig(inertia=0.6, alpha=0.25, beta=0.15, noise_std=0.0, max_step_delta=0.1)
    rng = random.Random(7)
    semantic_state = SemanticState(
        sentiment=0.4,
        stance=0.7,
        topic={"topic_0": 0.8, "topic_1": 0.2},
        embedding=[0.2, 0.1, -0.3, 0.4],
    )
    profile = {
        "efficiency": 0.9,
        "emotion": 0.6,
        "risk": 0.3,
        "conformity": 0.8,
    }

    next_state, attribution = heterogeneous_update_attitude(
        agent_profile=profile,
        agent_state=0.4,
        neighbors_state=0.6,
        semantic_state=semantic_state,
        config=cfg,
        rng=rng,
    )

    assert 0.0 <= next_state <= 1.0
    assert abs(next_state - 0.4) <= cfg.max_step_delta + 1e-9
    assert set(attribution.keys()) == {
        "self",
        "semantic",
        "neighbor",
        "noise",
        "self_contribution",
        "semantic_contribution",
        "neighbor_contribution",
        "noise_contribution",
    }
