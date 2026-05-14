"""Deterministic chief orchestrator wrapping MiroFishDiscussion."""

from __future__ import annotations

import io
import json
import sys
import time
import uuid
from contextlib import redirect_stdout
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO

from ..mirofish.discussion import DiscussionResult, MiroFishDiscussion
from ..reporting.deepseek_reporter import DeepSeekReporter
from ..research_agents.profiles import all_research_profiles
from ..research_agents.researcher import build_evidence_text, run_research_agent
from .chief_profile import CHIEF_PROFILE
from .planner import TaskGraph, build_task_graph
from .registry import get_domain_expert_entries
from .reporting import (
    serialize_agent_state,
    build_briefing_html,
    build_briefing_markdown,
    build_expert_output_summary,
    build_research_reports_file_markdown,
    detect_conflicts,
    detect_risk_notes,
    serialize_discussion_result,
    write_json,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _display_to_agent_id() -> dict[str, str]:
    return {row["display_name"]: row["agent_id"] for row in get_domain_expert_entries()}


def _edges_from_nodes(graph: TaskGraph) -> list[list[str]]:
    edges: list[list[str]] = []
    for n in graph.nodes:
        for dep in n.depends_on:
            edges.append([dep, n.task_id])
    return edges


def _per_expert_trace(
    dr: DiscussionResult,
    display_to_id: dict[str, str],
) -> dict[str, Any]:
    initial = dr.rounds[0].agent_states if dr.rounds else {}
    final = dr.rounds[-1].agent_states if dr.rounds else {}
    out: dict[str, Any] = {}
    for display_name, st_final in final.items():
        aid = display_to_id.get(display_name, "")
        st0 = initial.get(display_name)
        fc = dr.agent_forecasts.get(display_name, {})
        out[aid or display_name] = {
            "agent_id": aid,
            "display_name": display_name,
            "input_topic": dr.topic,
            "initial_state": serialize_agent_state(st0) if st0 else None,
            "final_state": serialize_agent_state(st_final) if st_final else None,
            "forecasts": dict(fc),
        }
    return out


def _emit(
    timeline: list[dict[str, Any]],
    *,
    t_ms: int,
    agent_id: str,
    display_name: str,
    phase: str,
    message: str,
    task_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    timeline.append(
        {
            "t_ms": t_ms,
            "agent_id": agent_id,
            "display_name": display_name,
            "phase": phase,
            "message": message,
            "task_id": task_id,
            "metadata": metadata or {},
        }
    )


def run_orchestrated_case(
    case_input: dict[str, Any],
    *,
    num_rounds: int = 3,
    verbose: bool = False,
    output_base: Path | None = None,
    deepseek_mode: str = "auto",
) -> dict[str, Any]:
    """
    Run chief planner + MiroFish per topic; write artifacts under artifacts/orchestrator_runs/<run_id>/.

    Parameters
    ----------
    case_input:
        Must include `data` dict for MiroFish. Optional: case_id, text|narrative, topic|topics.
    output_base:
        Defaults to <repo>/artifacts/orchestrator_runs
    """
    run_id = str(case_input.get("run_id") or uuid.uuid4().hex)
    base = output_base or (_repo_root() / "artifacts" / "orchestrator_runs")
    out_dir = base / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    started_iso = _utc_now_iso()
    t_wall0 = time.perf_counter()
    timeline: list[dict[str, Any]] = []

    _emit(
        timeline,
        t_ms=0,
        agent_id=CHIEF_PROFILE.agent_id,
        display_name=CHIEF_PROFILE.display_name,
        phase="start",
        message="Orchestrator run started",
        task_id=None,
        metadata={"run_id": run_id},
    )

    data = case_input.get("data")
    if not isinstance(data, dict):
        err = "case_input['data'] must be a dict for MiroFishDiscussion"
        trace = {
            "run_id": run_id,
            "schema_version": "1.0",
            "started_iso": started_iso,
            "ended_iso": _utc_now_iso(),
            "chief": asdict(CHIEF_PROFILE),
            "error": err,
        }
        write_json(out_dir / "orchestration_trace.json", trace)
        raise ValueError(err)

    graph = build_task_graph(case_input)
    _emit(
        timeline,
        t_ms=int((time.perf_counter() - t_wall0) * 1000),
        agent_id=CHIEF_PROFILE.agent_id,
        display_name=CHIEF_PROFILE.display_name,
        phase="plan",
        message=graph.chief_plan_summary,
        task_id="plan_topics",
        metadata={"topics": graph.topics},
    )

    topic_results: dict[str, DiscussionResult] = {}
    task_records: list[dict[str, Any]] = []
    display_to_id = _display_to_agent_id()

    # lightweight ingest/plan pseudo-tasks for trace completeness
    t_ingest_start = time.perf_counter()
    task_records.append(
        {
            "task_id": "ingest_case",
            "task_type": "ingest",
            "status": "completed",
            "started_ms": int((t_ingest_start - t_wall0) * 1000),
            "ended_ms": int((time.perf_counter() - t_wall0) * 1000),
            "error": None,
            "input": {"keys": sorted(case_input.keys())},
            "output": {"data_keys": sorted(data.keys())},
        }
    )
    t_plan_start = time.perf_counter()
    task_records.append(
        {
            "task_id": "plan_topics",
            "task_type": "plan",
            "status": "completed",
            "started_ms": int((t_plan_start - t_wall0) * 1000),
            "ended_ms": int((time.perf_counter() - t_wall0) * 1000),
            "error": None,
            "input": {"case_id": case_input.get("case_id")},
            "output": {"topics": graph.topics, "chief_plan_summary": graph.chief_plan_summary},
        }
    )

    evidence_text = build_evidence_text(case_input)
    research_reports_list: list[dict[str, Any]] = []
    t_research_panel = time.perf_counter()
    for profile in all_research_profiles():
        tid = f"research_{profile.agent_id}"
        _emit(
            timeline,
            t_ms=int((time.perf_counter() - t_wall0) * 1000),
            agent_id=profile.agent_id,
            display_name=profile.display_name,
            phase="research_assigned",
            message="Research briefing card assigned",
            task_id=tid,
            metadata={"focus": profile.research_focus},
        )
        _emit(
            timeline,
            t_ms=int((time.perf_counter() - t_wall0) * 1000),
            agent_id=profile.agent_id,
            display_name=profile.display_name,
            phase="research_working",
            message=f"Preparing {profile.title.lower()} evidence brief",
            task_id=tid,
            metadata={"focus": profile.research_focus},
        )
        row = run_research_agent(
            profile,
            case_input,
            evidence_text,
            model="deepseek-chat",
            deepseek_mode=deepseek_mode,
        )
        research_reports_list.append(row)
        end_phase = "research_failed" if row.get("status") == "failed" else "research_completed"
        _emit(
            timeline,
            t_ms=int((time.perf_counter() - t_wall0) * 1000),
            agent_id=profile.agent_id,
            display_name=profile.display_name,
            phase=end_phase,
            message="Research brief finalized" if end_phase == "research_completed" else "Research brief used fallback after LLM error",
            task_id=tid,
            metadata={"status": row.get("status"), "errors": row.get("errors") or []},
        )

    research_doc: dict[str, Any] = {
        "run_id": run_id,
        "chief": {
            "agent_id": CHIEF_PROFILE.agent_id,
            "display_name": CHIEF_PROFILE.display_name,
        },
        "reports": research_reports_list,
    }
    write_json(out_dir / "research_reports.json", research_doc)
    (out_dir / "research_reports.md").write_text(
        build_research_reports_file_markdown(
            run_id=run_id,
            chief=research_doc["chief"],
            reports=research_reports_list,
        ),
        encoding="utf-8",
    )

    task_records.append(
        {
            "task_id": "research_panel",
            "task_type": "research_briefings",
            "status": "completed",
            "started_ms": int((t_research_panel - t_wall0) * 1000),
            "ended_ms": int((time.perf_counter() - t_wall0) * 1000),
            "error": None,
            "input": {"evidence_chars": len(evidence_text)},
            "output": {"reports": research_reports_list},
        }
    )

    sink: TextIO | None = io.StringIO() if not verbose else None

    for topic in graph.topics:
        task_id = f"mirofish_discussion_{topic}"
        _emit(
            timeline,
            t_ms=int((time.perf_counter() - t_wall0) * 1000),
            agent_id=CHIEF_PROFILE.agent_id,
            display_name=CHIEF_PROFILE.display_name,
            phase="delegate",
            message=f"Dispatching MiroFish discussion for topic '{topic}'",
            task_id=task_id,
            metadata={"experts": list(display_to_id.keys())},
        )
        for row in get_domain_expert_entries():
            _emit(
                timeline,
                t_ms=int((time.perf_counter() - t_wall0) * 1000),
                agent_id=row["agent_id"],
                display_name=row["display_name"],
                phase="assign",
                message=f"Joined '{topic}' MiroFish track",
                task_id=task_id,
                metadata={"topic": topic},
            )

        engine = MiroFishDiscussion()
        t0 = time.perf_counter()
        err: str | None = None
        dr: DiscussionResult | None = None
        try:
            if sink is not None:
                with redirect_stdout(sink):
                    dr = engine.run_discussion(data, topic, num_rounds=num_rounds)
            else:
                dr = engine.run_discussion(data, topic, num_rounds=num_rounds)
        except Exception as exc:  # noqa: BLE001 — surfaced in trace
            err = f"{type(exc).__name__}: {exc}"
        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        if dr is not None:
            topic_results[topic] = dr
            for r in dr.rounds:
                _emit(
                    timeline,
                    t_ms=int((time.perf_counter() - t_wall0) * 1000),
                    agent_id=CHIEF_PROFILE.agent_id,
                    display_name=CHIEF_PROFILE.display_name,
                    phase="mirofish_round",
                    message=f"Completed discussion round {r.round_number} on {topic}",
                    task_id=task_id,
                    metadata={
                        "topic": topic,
                        "round": r.round_number,
                        "average_sentiment": r.average_sentiment,
                        "convergence_score": r.convergence_score,
                    },
                )

        task_records.append(
            {
                "task_id": task_id,
                "task_type": "mirofish_discussion",
                "status": "completed" if err is None else "failed",
                "started_ms": int((t0 - t_wall0) * 1000),
                "ended_ms": int((time.perf_counter() - t_wall0) * 1000),
                "duration_ms": elapsed_ms,
                "error": err,
                "input": {
                    "topic": topic,
                    "num_rounds": num_rounds,
                    "data_keys": sorted(data.keys()),
                },
                "output": None if dr is None else serialize_discussion_result(dr),
                "per_expert": None if dr is None else _per_expert_trace(dr, display_to_id),
            }
        )

    conflicts: list[str] = []
    risks: list[str] = []
    for dr in topic_results.values():
        conflicts.extend(detect_conflicts(dr))
        risks.extend(detect_risk_notes(dr))

    _emit(
        timeline,
        t_ms=int((time.perf_counter() - t_wall0) * 1000),
        agent_id=CHIEF_PROFILE.agent_id,
        display_name=CHIEF_PROFILE.display_name,
        phase="synthesize",
        message="Cross-topic synthesis complete",
        task_id="synthesize_cross_topic",
        metadata={"topics": list(topic_results.keys())},
    )

    t_syn_start = time.perf_counter()
    task_records.append(
        {
            "task_id": "synthesize_cross_topic",
            "task_type": "synthesize",
            "status": "completed",
            "started_ms": int((t_syn_start - t_wall0) * 1000),
            "ended_ms": int((time.perf_counter() - t_wall0) * 1000),
            "error": None,
            "input": {"topics": list(topic_results.keys())},
            "output": {"conflicts": conflicts, "risk_notes": risks},
        }
    )

    expert_summary = build_expert_output_summary(topic_results, display_to_id)

    deepseek_expansion: str | None = None
    deepseek_meta: dict[str, Any] = {"status": "skipped", "errors": []}
    briefing_core = build_briefing_markdown(
        case_input=case_input,
        task_graph=graph,
        topic_results=topic_results,
        conflicts=conflicts,
        risks=risks,
        expert_summary=expert_summary,
        deepseek_expansion=None,
        research_reports=research_reports_list,
    )
    reporter = DeepSeekReporter(mode=deepseek_mode)
    exp = reporter.expand_orchestrator_briefing(briefing_core)
    deepseek_meta = {"status": exp.get("status"), "errors": list(exp.get("errors") or [])}
    if exp.get("status") == "ok" and (exp.get("text") or "").strip():
        deepseek_expansion = str(exp["text"]).strip()
        _emit(
            timeline,
            t_ms=int((time.perf_counter() - t_wall0) * 1000),
            agent_id=CHIEF_PROFILE.agent_id,
            display_name=CHIEF_PROFILE.display_name,
            phase="deepseek",
            message="Optional narrative expansion completed",
            task_id=None,
            metadata={"chars": len(deepseek_expansion)},
        )
    elif exp.get("status") == "error":
        _emit(
            timeline,
            t_ms=int((time.perf_counter() - t_wall0) * 1000),
            agent_id=CHIEF_PROFILE.agent_id,
            display_name=CHIEF_PROFILE.display_name,
            phase="deepseek",
            message="DeepSeek expansion failed; deterministic briefing only",
            task_id=None,
            metadata={"errors": deepseek_meta.get("errors", [])},
        )

    briefing_md = build_briefing_markdown(
        case_input=case_input,
        task_graph=graph,
        topic_results=topic_results,
        conflicts=conflicts,
        risks=risks,
        expert_summary=expert_summary,
        deepseek_expansion=deepseek_expansion,
        research_reports=research_reports_list,
    )
    briefing_html = build_briefing_html(
        case_input=case_input,
        task_graph=graph,
        topic_results=topic_results,
        conflicts=conflicts,
        risks=risks,
        expert_summary=expert_summary,
        deepseek_expansion=deepseek_expansion,
        research_reports=research_reports_list,
    )

    (out_dir / "briefing_report.md").write_text(briefing_md, encoding="utf-8")
    (out_dir / "briefing_report.html").write_text(briefing_html, encoding="utf-8")

    ended_iso = _utc_now_iso()
    trace = {
        "run_id": run_id,
        "schema_version": "1.0",
        "started_iso": started_iso,
        "ended_iso": ended_iso,
        "chief": asdict(CHIEF_PROFILE),
        "case_input": case_input,
        "task_graph": {
            "chief_plan_summary": graph.chief_plan_summary,
            "topics": graph.topics,
            "nodes": [asdict(n) for n in graph.nodes],
            "edges": _edges_from_nodes(graph),
        },
        "tasks": task_records,
        "synthesis": {
            "conflicts": conflicts,
            "risk_notes": risks,
            "expert_summary": expert_summary,
        },
        "research_reports": research_doc,
        "deepseek": deepseek_meta,
    }
    write_json(out_dir / "orchestration_trace.json", trace)

    timeline_doc = {
        "run_id": run_id,
        "chief": {"agent_id": CHIEF_PROFILE.agent_id, "display_name": CHIEF_PROFILE.display_name},
        "started_iso": started_iso,
        "ended_iso": ended_iso,
        "events": timeline,
    }
    write_json(out_dir / "agent_timeline.json", timeline_doc)

    if verbose:
        print(json.dumps({"run_id": run_id, "artifacts_dir": str(out_dir)}, indent=2), file=sys.stderr)

    out_dir_s = str(out_dir)
    artifacts = {
        "run_dir": out_dir_s,
        "trace_json": str(out_dir / "orchestration_trace.json"),
        "timeline_json": str(out_dir / "agent_timeline.json"),
        "research_reports_json": str(out_dir / "research_reports.json"),
        "research_reports_md": str(out_dir / "research_reports.md"),
        "report_md": str(out_dir / "briefing_report.md"),
        "report_html": str(out_dir / "briefing_report.html"),
    }
    return {
        "run_id": run_id,
        "artifacts_dir": out_dir_s,
        "artifacts": artifacts,
        "topics": graph.topics,
        "topic_results": topic_results,
        "research_reports": research_reports_list,
        "trace_path": str(out_dir / "orchestration_trace.json"),
    }
