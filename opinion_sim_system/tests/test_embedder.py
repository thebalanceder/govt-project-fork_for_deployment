from ..models.embedding.embedder import Embedder


def test_embedder_returns_non_empty_vectors() -> None:
    embedder = Embedder(backend="hash", dimension=12)
    vectors = embedder.encode(["great battery life", "价格合理"])

    assert vectors.shape == (2, 12)
    assert vectors.any()
