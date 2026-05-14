"""Deterministic task planning for the chief orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_VALID_TOPICS = ("economic", "political", "cultural")


@dataclass
class TaskNode:
    task_id: str
    task_type: str
    topic: str | None
    depends_on: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class TaskGraph:
    chief_plan_summary: str
    topics: list[str]
    nodes: list[TaskNode]


def _normalize_topics(raw: Any) -> list[str]:
    if raw is None:
        return list(_VALID_TOPICS)
    if isinstance(raw, str):
        topics = [raw.strip().lower()]
    elif isinstance(raw, (list, tuple)):
        topics = [str(t).strip().lower() for t in raw]
    else:
        return list(_VALID_TOPICS)
    filtered = [t for t in topics if t in _VALID_TOPICS]
    # de-dupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for t in filtered:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out if out else list(_VALID_TOPICS)


def build_task_graph(case_input: dict[str, Any]) -> TaskGraph:
    """
    Build a deterministic task graph from case input.

    Supported keys:
    - topics: list[str] or topic: str — subset of economic|political|cultural
    - text / narrative — optional case narrative for logging and reports
    """
    topics = _normalize_topics(case_input.get("topics") or case_input.get("topic"))
    narrative = str(case_input.get("text") or case_input.get("narrative") or "").strip()
    case_id = str(case_input.get("case_id") or "").strip()

    chief_bits = [
        f"Selected topic tracks: {', '.join(topics)}.",
        "Each track will run the existing MiroFishDiscussion engine with all six domain experts.",
    ]
    if case_id:
        chief_bits.insert(0, f"Case reference: {case_id}.")
    if narrative:
        chief_bits.append("Case narrative captured for briefing context (deterministic routing only).")

    chief_plan_summary = " ".join(chief_bits)

    nodes: list[TaskNode] = [
        TaskNode(
            task_id="ingest_case",
            task_type="ingest",
            topic=None,
            depends_on=[],
            description="Validate case payload and derive topic routing.",
        ),
        TaskNode(
            task_id="plan_topics",
            task_type="plan",
            topic=None,
            depends_on=["ingest_case"],
            description="Deterministic topic selection for MiroFish runs.",
        ),
    ]
    for t in topics:
        nodes.append(
            TaskNode(
                task_id=f"mirofish_discussion_{t}",
                task_type="mirofish_discussion",
                topic=t,
                depends_on=["plan_topics"],
                description=f"Run MiroFish multi-agent discussion for '{t}' topic.",
            )
        )
    nodes.append(
        TaskNode(
            task_id="synthesize_cross_topic",
            task_type="synthesize",
            topic=None,
            depends_on=[f"mirofish_discussion_{t}" for t in topics],
            description="Aggregate consensus, conflicts, and risk notes across topic runs.",
        )
    )
    return TaskGraph(
        chief_plan_summary=chief_plan_summary,
        topics=topics,
        nodes=nodes,
    )
