"""Coverage validation using embedding-space clustering for Phase 1."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(slots=True)
class CoverageReport:
    n_samples: int
    n_clusters: int
    non_empty_clusters: int
    coverage_ratio: float


def _kmeans_assignments(
    embeddings: np.ndarray,
    n_clusters: int,
    max_iter: int = 20,
    seed: int = 42,
) -> np.ndarray:
    n_samples = embeddings.shape[0]
    k = min(n_clusters, n_samples)
    rng = np.random.default_rng(seed)

    initial_idx = rng.choice(n_samples, size=k, replace=False)
    centers = embeddings[initial_idx].copy()
    labels = np.zeros(n_samples, dtype=np.int64)

    for _ in range(max_iter):
        distances = np.linalg.norm(embeddings[:, None, :] - centers[None, :, :], axis=2)
        new_labels = np.argmin(distances, axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels

        for cluster_id in range(k):
            members = embeddings[labels == cluster_id]
            if members.size == 0:
                centers[cluster_id] = embeddings[rng.integers(0, n_samples)]
            else:
                centers[cluster_id] = members.mean(axis=0)

    return labels


def validate_cluster_coverage(embeddings: np.ndarray, n_clusters: int = 6) -> CoverageReport:
    """A lightweight deterministic k-means clustering coverage check."""
    if embeddings.ndim != 2:
        msg = "embeddings must be a 2D array"
        raise ValueError(msg)
    if embeddings.shape[0] == 0:
        return CoverageReport(0, n_clusters, 0, 0.0)

    labels = _kmeans_assignments(embeddings, n_clusters=n_clusters)
    non_empty = len(set(int(item) for item in labels.tolist()))
    ratio = non_empty / n_clusters
    return CoverageReport(
        n_samples=int(embeddings.shape[0]),
        n_clusters=n_clusters,
        non_empty_clusters=non_empty,
        coverage_ratio=ratio,
    )
