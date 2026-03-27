from ..simulation.network import build_network


def test_ring_network_has_two_neighbors() -> None:
    groups = ["a", "b", "c", "d"]
    adjacency = build_network(groups, topology="ring")

    assert set(adjacency["a"]) == {"b", "d"}
    assert set(adjacency["c"]) == {"b", "d"}
