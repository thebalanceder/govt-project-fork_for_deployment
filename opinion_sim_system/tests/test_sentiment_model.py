from ..models.sentiment.sentiment_model import SentimentModel


def test_sentiment_model_labels_positive_and_negative() -> None:
    model = SentimentModel(backend="lexicon")
    results = model.analyze(["excellent and smooth", "slow and confusing"])

    assert results[0].label == "POSITIVE"
    assert results[1].label == "NEGATIVE"
