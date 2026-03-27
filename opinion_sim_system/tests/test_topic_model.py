import unittest

from ..models.topic.topic_model import TopicModel


def test_topic_model_produces_topics() -> None:
    model = TopicModel(backend="keyword")
    docs = [
        "battery life is great",
        "setup process is confusing",
        "battery and price are both good",
    ]

    topics, topic_words = model.fit_transform(docs)
    assert len(topics) == len(docs)
    assert topic_words


def test_topic_model_bertopic_path_when_available() -> None:
    try:
        model = TopicModel(backend="bertopic")
    except Exception as exc:  # defensive, should not happen with current adapter
        raise AssertionError(f"TopicModel init failed unexpectedly: {exc}") from exc

    if model.backend != "bertopic":
        raise unittest.SkipTest("BERTopic is not available in this environment")

    docs = [
        "battery performance and charging speed are excellent",
        "pricing and cost-effectiveness are very important",
        "customer support response was slow and confusing",
        "battery lasts long and overall quality is stable",
    ]
    topics, topic_words = model.fit_transform(docs)
    assert len(topics) == len(docs)
    assert topic_words
