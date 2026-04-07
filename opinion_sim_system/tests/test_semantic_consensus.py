from ..models.semantic_fusion import resolve_expert_consensus
from ..models.task_experts.base import TaskExpertOutput


def _expert(name: str, score: float, confidence: float = 0.8, label: str = "X") -> TaskExpertOutput:
    return TaskExpertOutput(name=name, label=label, score=score, confidence=confidence)


def test_consensus_averages_when_spread_is_small() -> None:
    outputs = {
        "sentiment": _expert("sentiment", 0.20),
        "acceptance": _expert("acceptance", 0.62),
        "emotion": _expert("emotion", 0.18),
        "topic": _expert("topic", 0.61),
        "conflict": _expert("conflict", 0.63),
        "frame": _expert("frame", 0.60),
    }

    consensus = resolve_expert_consensus(outputs, api_key="test-key", threshold=0.2)

    assert consensus["method"] == "average"
    expected = (0.60 + 0.62 + 0.59 + 0.61 + 0.63 + 0.60) / 6
    assert abs(consensus["score"] - expected) < 1e-9
    assert consensus["spread"] < 0.2


def test_consensus_prefers_deepseek_on_high_spread(monkeypatch) -> None:
    outputs = {
        "sentiment": _expert("sentiment", -0.8),
        "acceptance": _expert("acceptance", 0.95),
        "emotion": _expert("emotion", 0.9),
        "topic": _expert("topic", 0.15),
        "conflict": _expert("conflict", 0.05),
        "frame": _expert("frame", 0.92),
    }

    monkeypatch.setattr(
        "opinion_sim_system.models.semantic_fusion._call_deepseek_consensus",
        lambda prompt, api_key, timeout_seconds=20.0: '{"final_score": 0.88, "reason": "DeepSeek arbitration"}',
    )

    consensus = resolve_expert_consensus(outputs, api_key="test-key", threshold=0.2)

    assert consensus["method"] == "deepseek"
    assert consensus["score"] == 0.88
    assert consensus["spread"] > 0.2
