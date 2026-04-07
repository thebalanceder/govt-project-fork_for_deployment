"""Fusion logic for converting task-expert outputs into SemanticState."""

from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib import error, request

from .semantic_state import SemanticState
from .task_experts.base import TaskExpertOutput


CONSENSUS_SPREAD_THRESHOLD = 0.2
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"


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


def _normalize_score(expert_name: str, output: TaskExpertOutput) -> float:
    try:
        score = float(output.score)
    except (TypeError, ValueError):
        return 0.5
    if expert_name in {"sentiment", "emotion"}:
        return max(0.0, min(1.0, (score + 1.0) / 2.0))
    if expert_name == "conflict":
        return max(0.0, min(1.0, 1.0 - score))
    if expert_name == "frame":
        return max(0.0, min(1.0, abs(score)))
    return max(0.0, min(1.0, score))


def _extract_scores(expert_outputs: dict[str, TaskExpertOutput]) -> dict[str, float]:
    ordered_names = ("sentiment", "acceptance", "emotion", "conflict", "frame")
    scores: dict[str, float] = {}
    for expert_name in ordered_names:
        output = expert_outputs.get(expert_name)
        if isinstance(output, TaskExpertOutput):
            try:
                scores[expert_name] = _normalize_score(expert_name, output)
            except Exception:
                scores[expert_name] = 0.5
    return scores


def _clean_json_text(text: str) -> str:
    trimmed = text.strip()
    if trimmed.startswith("```"):
        trimmed = re.sub(r"^```(?:json)?\s*", "", trimmed, flags=re.IGNORECASE)
        trimmed = re.sub(r"\s*```$", "", trimmed)
    return trimmed.strip()


def _parse_deepseek_score(text: str) -> float:
    cleaned = _clean_json_text(text)
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            candidate = parsed.get("final_score", parsed.get("score"))
            if isinstance(candidate, (int, float)):
                return max(0.0, min(1.0, float(candidate)))
        elif isinstance(parsed, (int, float)):
            return max(0.0, min(1.0, float(parsed)))
    except json.JSONDecodeError:
        pass

    match = re.search(r"(-?\d+(?:\.\d+)?)", cleaned)
    if match:
        return max(0.0, min(1.0, float(match.group(1))))
    raise ValueError("DeepSeek response did not contain a valid score")


def _call_deepseek_consensus(prompt: str, api_key: str, timeout_seconds: float = 20.0) -> str:
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "You return a single consensus score as compact JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=f"{DEEPSEEK_API_BASE.rstrip('/')}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=timeout_seconds) as response:
        content = response.read().decode("utf-8")
    parsed = json.loads(content)
    choices = parsed.get("choices", [])
    if not choices:
        raise RuntimeError("DeepSeek response missing choices")
    message = choices[0].get("message", {})
    text = str(message.get("content", "")).strip()
    if not text:
        raise RuntimeError("DeepSeek response content is empty")
    return text


def resolve_expert_consensus(
    expert_outputs: dict[str, TaskExpertOutput],
    *,
    case_text: str = "",
    api_key: str | None = None,
    threshold: float = CONSENSUS_SPREAD_THRESHOLD,
    timeout_seconds: float = 20.0,
) -> dict[str, Any]:
    scores = _extract_scores(expert_outputs)
    if not scores:
        return {
            "score": 0.5,
            "method": "fallback-average",
            "spread": 0.0,
            "threshold": threshold,
            "source_scores": {},
        }

    score_values = list(scores.values())
    spread = max(score_values) - min(score_values)
    average = sum(score_values) / len(score_values)
    consensus = {
        "score": float(max(0.0, min(1.0, average))),
        "method": "average" if spread <= threshold else "fallback-average",
        "spread": float(spread),
        "threshold": float(threshold),
        "source_scores": scores,
    }

    if spread <= threshold:
        return consensus

    resolved_api_key = api_key if api_key is not None else os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not resolved_api_key:
        return consensus

    prompt_expert_scores: list[dict[str, Any]] = []
    for expert_name, score in scores.items():
        output = expert_outputs.get(expert_name)
        if not isinstance(output, TaskExpertOutput):
            continue
        try:
            confidence = float(output.confidence)
        except (TypeError, ValueError):
            confidence = 0.0
        prompt_expert_scores.append(
            {
                "expert": expert_name,
                "score": float(score),
                "label": str(output.label),
                "confidence": confidence,
            }
        )

    if not prompt_expert_scores:
        return consensus

    prompt_obj: dict[str, Any] = {
        "task": (
            "You are judging PUBLIC ACCEPTANCE of the case below. "
            "Score 0 = the public would strongly reject this; "
            "Score 1 = the public would strongly accept this. "
            "Consider the case content itself, not just the expert numbers."
        ),
        "rule": {
            "low_spread": "average the expert scores",
            "high_spread": "return a single consensus score between 0 and 1",
            "threshold": threshold,
        },
        "expert_scores": prompt_expert_scores,
        "output_format": {
            "final_score": "number between 0 and 1",
            "reason": "short string",
        },
    }
    if case_text:
        prompt_obj["case_text"] = case_text[:500]
    prompt = json.dumps(prompt_obj, ensure_ascii=False)

    try:
        text = _call_deepseek_consensus(prompt=prompt, api_key=resolved_api_key, timeout_seconds=timeout_seconds)
        final_score = _parse_deepseek_score(text)
        consensus.update(
            {
                "score": final_score,
                "method": "deepseek",
                "deepseek_response": text,
            }
        )
        return consensus
    except Exception:
        return consensus


def fuse_semantic_state(
    expert_outputs: dict[str, TaskExpertOutput],
    embedding: list[float],
    case_text: str = "",
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

    consensus = resolve_expert_consensus(expert_outputs, case_text=case_text)
    stance = float(max(0.0, min(1.0, consensus["score"])))

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
            "consensus": consensus,
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
