"""Simple network topology helpers for group interaction."""

from __future__ import annotations


def build_network(groups: list[str], topology: str = "fully_connected") -> dict[str, list[str]]:
    """Build adjacency map for either fully connected or ring topology."""
    if not groups:
        return {}

    if topology == "fully_connected":
        return {group: [other for other in groups if other != group] for group in groups}

    if topology == "ring":
        n = len(groups)
        adjacency: dict[str, list[str]] = {}
        for idx, group in enumerate(groups):
            left = groups[(idx - 1) % n]
            right = groups[(idx + 1) % n]
            adjacency[group] = [left, right] if left != right else [left]
        return adjacency

    msg = f"Unsupported topology: {topology}"
    raise ValueError(msg)


def neighbor_mean(group: str, adjacency: dict[str, list[str]], states: dict[str, float]) -> float:
    """Compute mean attitude of group neighbors."""
    neighbors = adjacency.get(group, [])
    if not neighbors:
        return states[group]
    total = sum(states[neighbor] for neighbor in neighbors)
    return total / len(neighbors)
