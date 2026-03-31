import random
import unittest

from ..simulation.update_rules import UpdateConfig, update_attitude


def test_update_rule_without_noise_is_deterministic() -> None:
    cfg = UpdateConfig(inertia=0.6, alpha=0.25, beta=0.15, noise_std=0.0)
    rng = random.Random(7)

    state = update_attitude(0.8, 0.7, 0.6, cfg, rng)
    # Expected: 0.6*0.8 + 0.25*0.7 + 0.15*0.6 = 0.48 + 0.175 + 0.09 = 0.745
    assert abs(state - 0.745) < 1e-9


def test_invalid_update_config_raises() -> None:
    with unittest.TestCase().assertRaisesRegex(ValueError, "non-negative"):
        UpdateConfig(inertia=-0.1)
