from ..archetypes.profiles import DIMENSIONS, get_default_profiles


def test_profiles_contains_six_groups_and_dimensions() -> None:
    profiles = get_default_profiles()
    assert len(profiles) == 6

    for weights in profiles.values():
        assert set(weights.keys()) == set(DIMENSIONS)
