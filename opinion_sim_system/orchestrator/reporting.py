"""Artifact writers: trace JSON, Markdown/HTML briefing, agent timeline."""

from __future__ import annotations

import html as html_module
import json
from pathlib import Path
from typing import Any

from ..agents.base_agent import AgentState
from ..mirofish.discussion import DiscussionResult, DiscussionRound
from .chief_profile import CHIEF_PROFILE
from .planner import TaskGraph


def serialize_agent_state(state: AgentState) -> dict[str, Any]:
    return {
        "topic": state.topic,
        "sentiment": state.sentiment,
        "confidence": state.confidence,
        "key_factors": list(state.key_factors),
        "reasoning": state.reasoning,
        "forecast_7d": state.forecast_7d,
        "forecast_30d": state.forecast_30d,
        "timestamp": state.timestamp.isoformat(),
    }


def _serialize_round(r: DiscussionRound) -> dict[str, Any]:
    return {
        "round_number": r.round_number,
        "agent_states": {k: serialize_agent_state(v) for k, v in r.agent_states.items()},
        "responses": list(r.responses),
        "average_sentiment": r.average_sentiment,
        "convergence_score": r.convergence_score,
        "timestamp": r.timestamp.isoformat(),
    }


def serialize_discussion_result(dr: DiscussionResult) -> dict[str, Any]:
    return {
        "topic": dr.topic,
        "rounds": [_serialize_round(x) for x in dr.rounds],
        "final_consensus": dr.final_consensus,
        "convergence_rate": dr.convergence_rate,
        "agent_forecasts": dr.agent_forecasts,
        "explanation": dr.explanation,
        "timestamp": dr.timestamp.isoformat(),
    }


def detect_conflicts(dr: DiscussionResult) -> list[str]:
    notes: list[str] = []
    if dr.convergence_rate < 0.55:
        notes.append(
            f"Low convergence on {dr.topic} track (convergence_rate={dr.convergence_rate:.2f})."
        )
    final = dr.rounds[-1].agent_states if dr.rounds else {}
    if final:
        vals = [s.sentiment for s in final.values()]
        spread = max(vals) - min(vals)
        if spread > 0.85:
            notes.append(f"Wide expert sentiment spread on {dr.topic} (max-min={spread:.2f}).")
    return notes


def detect_risk_notes(dr: DiscussionResult) -> list[str]:
    risks: list[str] = []
    if dr.final_consensus < -0.15 and dr.convergence_rate < 0.6:
        risks.append(
            f"Negative consensus with weak alignment on {dr.topic}: monitor escalation and trust metrics."
        )
    if dr.convergence_rate > 0.75 and dr.final_consensus > 0.35:
        risks.append(
            f"Strong agreement on {dr.topic}: watch for blind spots / missing contrarian evidence in inputs."
        )
    return risks


def final_recommendation_line(topic_results: dict[str, DiscussionResult]) -> str:
    bits: list[str] = []
    for topic, r in topic_results.items():
        label = "positive" if r.final_consensus > 0.1 else "negative" if r.final_consensus < -0.1 else "neutral"
        bits.append(
            f"{topic}: {label} consensus ({r.final_consensus:.2f}), convergence {r.convergence_rate:.0%}"
        )
    return (
        "Monitor evidence updates and rerun MiroFish tracks if new high-salience items arrive. "
        "Current posture — " + "; ".join(bits) + "."
    )


def build_expert_output_summary(
    topic_results: dict[str, DiscussionResult],
    display_to_agent_id: dict[str, str],
) -> dict[str, dict[str, Any]]:
    """Per display_name aggregate across topics."""
    acc: dict[str, dict[str, Any]] = {}
    for topic, dr in topic_results.items():
        final_states = dr.rounds[-1].agent_states if dr.rounds else {}
        forecasts = dr.agent_forecasts
        for display_name, state in final_states.items():
            aid = display_to_agent_id.get(display_name, "")
            row = acc.setdefault(
                display_name,
                {
                    "agent_id": aid,
                    "display_name": display_name,
                    "by_topic": {},
                },
            )
            fc = forecasts.get(display_name, {})
            row["by_topic"][topic] = {
                "final_sentiment": state.sentiment,
                "confidence": state.confidence,
                "forecast_7d": fc.get("forecast_7d"),
                "forecast_30d": fc.get("forecast_30d"),
                "key_factors": list(state.key_factors),
            }
    return acc


def build_briefing_markdown(
    *,
    case_input: dict[str, Any],
    task_graph: TaskGraph,
    topic_results: dict[str, DiscussionResult],
    conflicts: list[str],
    risks: list[str],
    expert_summary: dict[str, dict[str, Any]],
    deepseek_expansion: str | None,
) -> str:
    lines: list[str] = []
    lines.append("# Decision briefing (orchestrated run)")
    lines.append("")
    lines.append("## Case input")
    lines.append("```json")
    lines.append(json.dumps(case_input, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## Chief plan")
    lines.append(
        f"**{CHIEF_PROFILE.display_name}** ({CHIEF_PROFILE.title}): {task_graph.chief_plan_summary}"
    )
    lines.append("")
    lines.append("## Task decomposition")
    for n in task_graph.nodes:
        dep = ", ".join(n.depends_on) if n.depends_on else "—"
        topic = n.topic or "—"
        lines.append(f"- `{n.task_id}` | type={n.task_type} | topic={topic} | depends=[{dep}] — {n.description}")
    lines.append("")
    lines.append("## Each Dr. / domain expert output summary")
    for display_name in sorted(expert_summary.keys()):
        row = expert_summary[display_name]
        lines.append(f"### {display_name} (`{row.get('agent_id', '')}`)")
        for topic, payload in row["by_topic"].items():
            lines.append(
                f"- **{topic}**: sentiment={payload['final_sentiment']:.3f}, "
                f"confidence={payload['confidence']:.2f}, "
                f"7d={payload.get('forecast_7d')}, 30d={payload.get('forecast_30d')}; "
                f"factors: {', '.join(payload.get('key_factors') or [])}"
            )
        lines.append("")
    lines.append("## Consensus")
    for topic, dr in topic_results.items():
        lines.append(
            f"- **{topic}**: final_consensus={dr.final_consensus:.3f}, "
            f"convergence_rate={dr.convergence_rate:.3f}"
        )
    lines.append("")
    lines.append("## Conflicts")
    if conflicts:
        for c in conflicts:
            lines.append(f"- {c}")
    else:
        lines.append("- No major conflict flags under deterministic rules.")
    lines.append("")
    lines.append("## Risk notes")
    if risks:
        for r in risks:
            lines.append(f"- {r}")
    else:
        lines.append("- No additional deterministic risk flags.")
    lines.append("")
    lines.append("## Final recommendation")
    lines.append(final_recommendation_line(topic_results))
    lines.append("")
    if deepseek_expansion:
        lines.append("## Optional narrative expansion (DeepSeek)")
        lines.append(deepseek_expansion)
        lines.append("")
    return "\n".join(lines)


def build_briefing_html(
    *,
    case_input: dict[str, Any],
    task_graph: TaskGraph,
    topic_results: dict[str, DiscussionResult],
    conflicts: list[str],
    risks: list[str],
    expert_summary: dict[str, dict[str, Any]],
    deepseek_expansion: str | None,
) -> str:
    def esc(x: Any) -> str:
        return html_module.escape(str(x), quote=True)

    body_parts: list[str] = []
    body_parts.append("<h1>Decision briefing (orchestrated run)</h1>")
    body_parts.append("<h2>Case input</h2><pre>")
    body_parts.append(esc(json.dumps(case_input, ensure_ascii=False, indent=2)))
    body_parts.append("</pre>")
    body_parts.append("<h2>Chief plan</h2><p>")
    body_parts.append(
        f"<strong>{esc(CHIEF_PROFILE.display_name)}</strong> ({esc(CHIEF_PROFILE.title)}): "
        f"{esc(task_graph.chief_plan_summary)}</p>"
    )
    body_parts.append("<h2>Task decomposition</h2><ul>")
    for n in task_graph.nodes:
        dep = ", ".join(n.depends_on) if n.depends_on else "—"
        topic = n.topic or "—"
        body_parts.append(
            f"<li><code>{esc(n.task_id)}</code> — type={esc(n.task_type)}, topic={esc(topic)}, "
            f"depends=[{esc(dep)}] — {esc(n.description)}</li>"
        )
    body_parts.append("</ul>")
    body_parts.append("<h2>Expert output summary</h2>")
    for display_name in sorted(expert_summary.keys()):
        row = expert_summary[display_name]
        body_parts.append(f"<h3>{esc(display_name)} (<code>{esc(row.get('agent_id',''))}</code>)</h3><ul>")
        for topic, payload in row["by_topic"].items():
            factors = ", ".join(payload.get("key_factors") or [])
            body_parts.append(
                "<li>"
                f"<strong>{esc(topic)}</strong>: sentiment={payload['final_sentiment']:.3f}, "
                f"confidence={payload['confidence']:.2f}, "
                f"7d={esc(payload.get('forecast_7d'))}, 30d={esc(payload.get('forecast_30d'))}; "
                f"factors: {esc(factors)}"
                "</li>"
            )
        body_parts.append("</ul>")
    body_parts.append("<h2>Consensus</h2><ul>")
    for topic, dr in topic_results.items():
        body_parts.append(
            f"<li><strong>{esc(topic)}</strong>: final_consensus={dr.final_consensus:.3f}, "
            f"convergence_rate={dr.convergence_rate:.3f}</li>"
        )
    body_parts.append("</ul><h2>Conflicts</h2><ul>")
    for c in conflicts or ["No major conflict flags under deterministic rules."]:
        body_parts.append(f"<li>{esc(c)}</li>")
    body_parts.append("</ul><h2>Risk notes</h2><ul>")
    for r in risks or ["No additional deterministic risk flags."]:
        body_parts.append(f"<li>{esc(r)}</li>")
    body_parts.append("</ul><h2>Final recommendation</h2><p>")
    body_parts.append(esc(final_recommendation_line(topic_results)))
    body_parts.append("</p>")
    if deepseek_expansion:
        body_parts.append("<h2>Optional narrative expansion (DeepSeek)</h2><p>")
        body_parts.append(esc(deepseek_expansion))
        body_parts.append("</p>")
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Briefing</title>"
        "<style>body{font-family:system-ui,Segoe UI,Roboto,sans-serif;margin:2rem;line-height:1.45}"
        "pre{background:#f6f8fa;padding:1rem;overflow:auto}code{background:#eef;padding:0 4px}</style>"
        "</head><body>"
        + "".join(body_parts)
        + "</body></html>"
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
