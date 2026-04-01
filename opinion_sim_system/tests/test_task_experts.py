from ..models.task_experts import (
    EmotionExpert,
    RiskExpert,
    SentimentExpert,
    StanceExpert,
    TaskExpertInput,
    TopicExpert,
    ValueFrameExpert,
)


def test_task_experts_produce_structured_outputs() -> None:
    data = TaskExpertInput(
        product_description="Reliable product with fair price but confusing setup",
        comments=[
            "great battery and stable performance",
            "setup process is confusing",
            "价格合理，整体不错",
        ],
    )

    outputs = [
        SentimentExpert(backend="lexicon").analyze(data),
        StanceExpert().analyze(data),
        EmotionExpert().analyze(data),
        TopicExpert(backend="keyword").analyze(data),
        RiskExpert().analyze(data),
        ValueFrameExpert().analyze(data),
    ]

    assert len(outputs) == 6
    for item in outputs:
        assert isinstance(item.name, str)
        assert isinstance(item.label, str)
        assert isinstance(item.score, float)
        assert isinstance(item.confidence, float)
        assert isinstance(item.payload, dict)
