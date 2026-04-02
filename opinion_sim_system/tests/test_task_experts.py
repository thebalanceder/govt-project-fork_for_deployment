from ..models.task_experts import (
    AcceptanceExpert,
    ConflictExpert,
    EmotionExpert,
    FrameExpert,
    SentimentExpert,
    TaskExpertInput,
    TopicExpert,
)


def test_task_experts_produce_structured_outputs() -> None:
    data = TaskExpertInput(
        text="Reliable product with fair price but confusing setup",
        target="home device",
        domain="product",
        comments=[
            "great battery and stable performance",
            "setup process is confusing",
            "价格合理，整体不错",
        ],
    )

    outputs = [
        SentimentExpert(backend="lexicon").analyze(data),
        AcceptanceExpert().analyze(data),
        EmotionExpert().analyze(data),
        TopicExpert(backend="keyword").analyze(data),
        ConflictExpert().analyze(data),
        FrameExpert().analyze(data),
    ]

    assert len(outputs) == 6
    for item in outputs:
        assert isinstance(item.name, str)
        assert isinstance(item.label, str)
        assert isinstance(item.score, float)
        assert isinstance(item.confidence, float)
        assert isinstance(item.payload, dict)
