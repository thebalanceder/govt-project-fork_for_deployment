import numpy as np

from ..archetypes.clustering import validate_cluster_coverage


def test_validate_cluster_coverage_returns_valid_report() -> None:
    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.9, 0.1, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.9, 0.1],
            [0.0, 0.0, 1.0],
            [0.1, 0.0, 0.9],
        ],
        dtype=np.float64,
    )
    report = validate_cluster_coverage(embeddings, n_clusters=3)

    assert report.n_samples == 6
    assert report.n_clusters == 3
    assert 1 <= report.non_empty_clusters <= 3
    assert 0.0 <= report.coverage_ratio <= 1.0
