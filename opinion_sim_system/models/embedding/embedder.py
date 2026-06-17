"""Embedding abstraction for Phase 1.

Uses sentence-transformers when available; otherwise falls back to a deterministic
hash embedding backend so tests and local runs can execute offline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Iterable

import numpy as np

from ..hf_runtime import hf_models_enabled


def _normalize(text: str) -> list[str]:
    tokens = [tok.strip().lower() for tok in text.replace("\n", " ").split(" ")]
    return [tok for tok in tokens if tok]


def _hash_vector(text: str, dimension: int) -> np.ndarray:
    vector = np.zeros(dimension, dtype=np.float64)
    for token in _normalize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], byteorder="little", signed=False) % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[idx] += sign

    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


@dataclass(slots=True)
class Embedder:
    """Sentence embedding adapter with deterministic fallback."""

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    backend: str = "auto"
    dimension: int = 24
    _model: object | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self._model = None
        use_transformer = self.backend == "sentence-transformers" or (
            self.backend == "auto" and hf_models_enabled()
        )
        if use_transformer:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore

                self._model = SentenceTransformer(self.model_name)
                self.backend = "sentence-transformers"
            except Exception:
                self._model = None
                self.backend = "hash"
        else:
            self.backend = "hash"

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        """Encode a list of text items into a 2D embedding array."""
        text_list = [str(item) if item is not None else "" for item in texts]
        if not text_list:
            return np.zeros((0, self.dimension), dtype=np.float64)

        if self._model is not None:
            encode_method = getattr(self._model, "encode", None)
            if callable(encode_method):
                embeddings = encode_method(text_list, convert_to_numpy=True)
                return np.asarray(embeddings, dtype=np.float64)

        matrix = np.vstack([_hash_vector(text, self.dimension) for text in text_list])
        return matrix
