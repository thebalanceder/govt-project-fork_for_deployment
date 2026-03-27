"""Topic modeling adapter for Phase 1.

Supports BERTopic when available, with a deterministic keyword fallback.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
from typing import Iterable


TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)
STOPWORDS = {
    "the",
    "and",
    "is",
    "to",
    "a",
    "of",
    "in",
    "it",
    "i",
    "会",
    "很",
    "但",
    "了",
}


@dataclass(slots=True)
class TopicResult:
    topic_id: int
    topic_label: str
    probability: float


def _extract_tokens(text: str) -> list[str]:
    tokens = [tok.lower() for tok in TOKEN_RE.findall(text)]
    return [tok for tok in tokens if tok not in STOPWORDS and len(tok) > 1]


class TopicModel:
    """Topic model adapter with BERTopic optional backend."""

    def __init__(self, backend: str = "auto", min_topic_size: int = 2) -> None:
        self.backend = backend
        self.min_topic_size = min_topic_size
        self._model = None

        if backend in {"auto", "bertopic"}:
            try:
                from bertopic import BERTopic  # type: ignore

                self._model = BERTopic(min_topic_size=min_topic_size, calculate_probabilities=True)
                self.backend = "bertopic"
            except Exception:
                self._model = None
                self.backend = "keyword"
        else:
            self.backend = "keyword"

    def fit_transform(self, documents: Iterable[str]) -> tuple[list[TopicResult], dict[int, list[str]]]:
        docs = [str(item) if item is not None else "" for item in documents]
        if not docs:
            return [], {}

        if self._model is not None:
            topics, probabilities = self._model.fit_transform(docs)
            info = self._model.get_topic_info()
            topic_labels: dict[int, str] = {}
            for _, row in info.iterrows():
                topic_labels[int(row["Topic"])] = str(row["Name"])

            results: list[TopicResult] = []
            for index, topic_id in enumerate(topics):
                topic_prob = float(probabilities[index].max()) if probabilities is not None else 1.0
                results.append(
                    TopicResult(
                        topic_id=int(topic_id),
                        topic_label=topic_labels.get(int(topic_id), f"topic_{topic_id}"),
                        probability=topic_prob,
                    )
                )

            topic_words: dict[int, list[str]] = {}
            for topic_id in sorted(set(int(item) for item in topics if int(item) >= 0)):
                words = self._model.get_topic(topic_id) or []
                topic_words[topic_id] = [str(word) for word, _ in words[:5]]
            return results, topic_words

        vocab = Counter()
        tokenized_docs: list[list[str]] = []
        for doc in docs:
            tokens = _extract_tokens(doc)
            tokenized_docs.append(tokens)
            vocab.update(tokens)

        top_terms = [word for word, _ in vocab.most_common(3)] or ["general"]
        topic_words = {idx: [term] for idx, term in enumerate(top_terms)}

        results: list[TopicResult] = []
        for tokens in tokenized_docs:
            if not tokens:
                results.append(TopicResult(topic_id=0, topic_label="general", probability=1.0))
                continue

            counts = [sum(1 for token in tokens if token == term) for term in top_terms]
            if max(counts) == 0:
                results.append(TopicResult(topic_id=0, topic_label="general", probability=1.0))
                continue

            topic_id = int(max(range(len(counts)), key=lambda i: counts[i]))
            probability = counts[topic_id] / max(len(tokens), 1)
            results.append(TopicResult(topic_id=topic_id, topic_label=top_terms[topic_id], probability=probability))

        return results, topic_words
