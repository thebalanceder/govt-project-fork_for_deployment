"""Fusion logic for converting task-expert outputs into SemanticState."""

from __future__ import annotations

from typing import Any

from .semantic_state import SemanticState
from .task_experts.base import TaskExpertOutput


def _normalized_topic(payload: dict[str, Any]) -> dict[str, float]:
    candidate = payload.get("distribution", {})
    if not isinstance(candidate, dict) or not candidate:
        return {"topic_0": 1.0}

    total = 0.0
    cleaned: dict[str, float] = {}
    for key, value in candidate.items():
        prob = max(0.0, float(value))
        cleaned[str(key)] = prob
        total += prob

    if total <= 0:
        return {"topic_0": 1.0}
    return {key: value / total for key, value in cleaned.items()}


def _expert_dict(output: TaskExpertOutput) -> dict[str, Any]:
    return {
        "label": output.label,
        "score": float(output.score),
        "confidence": float(output.confidence),
        "payload": output.payload,
    }


def fuse_semantic_state(
    expert_outputs: dict[str, TaskExpertOutput],
    embedding: list[float],
) -> SemanticState:
    sentiment_out = expert_outputs["sentiment"]
    acceptance_out = expert_outputs["acceptance"]
    topic_out = expert_outputs["topic"]
    conflict_out = expert_outputs["conflict"]
    frame_out = expert_outputs["frame"]
    emotion_out = expert_outputs["emotion"]

    sentiment = float(max(-1.0, min(1.0, sentiment_out.score)))
    sentiment_component = (sentiment + 1.0) / 2.0
    conflict_component = 1.0 - float(max(0.0, min(1.0, conflict_out.score)))
    acceptance_component = float(max(0.0, min(1.0, acceptance_out.score)))

    stance = 0.5 * acceptance_component + 0.3 * sentiment_component + 0.2 * conflict_component
    stance = float(max(0.0, min(1.0, stance)))

    topic = _normalized_topic(topic_out.payload)

    evidence_trace: dict[str, Any] = {
        "experts": {
            "sentiment": _expert_dict(sentiment_out),
            "acceptance": _expert_dict(acceptance_out),
            "emotion": _expert_dict(emotion_out),
            "topic": _expert_dict(topic_out),
            "conflict": _expert_dict(conflict_out),
            "frame": _expert_dict(frame_out),
        },
        "fusion": {
            "stance_components": {
                "acceptance_expert": acceptance_component,
                "sentiment_component": sentiment_component,
                "conflict_component": conflict_component,
            },
            "weights": {
                "acceptance_expert": 0.5,
                "sentiment_component": 0.3,
                "conflict_component": 0.2,
            },
        },
    }

    # Compatibility aliases for downstream consumers migrating from older naming.
    experts = evidence_trace["experts"]
    experts["stance"] = experts["acceptance"]
    experts["risk"] = experts["conflict"]
    experts["value_frame"] = experts["frame"]

    return SemanticState(
        sentiment=sentiment,
        stance=stance,
        topic=topic,
        embedding=embedding,
        evidence_trace=evidence_trace,
    )
