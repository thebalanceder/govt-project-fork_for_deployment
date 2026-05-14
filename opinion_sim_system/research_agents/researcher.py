"""Research briefing agents: optional DeepSeek, deterministic fallback, never raises."""

from __future__ import annotations

import json
from typing import Any

from ..reporting.deepseek_reporter import DeepSeekReporter
from .profiles import ResearchAgentProfile, all_research_profiles
from .prompts import RESEARCH_REPORT_PROMPT
from .schema import ResearchReport, ResearchRunResult

_RESEARCH_SYSTEM = (
    "You write short internal expert research briefings for government and institutional decision support. "
    "You follow the user's structure exactly and never fabricate citations or data not present in the prompt."
)


def build_agent_prompt(profile: ResearchAgentProfile, case_input: dict[str, Any], evidence_text: str) -> str:
    """Full user prompt for one research agent."""
    meta = {k: v for k, v in case_input.items() if k != "data"}
    meta_json = json.dumps(meta, ensure_ascii=False, indent=2) if meta else "{}"
    data_obj = case_input.get("data")
    data_json = (
        json.dumps(data_obj, ensure_ascii=False, indent=2)[:80000]
        if isinstance(data_obj, dict)
        else "null"
    )
    case_and_evidence = (
        f"#### Case metadata (excluding raw `data`)\n```json\n{meta_json}\n```\n\n"
        f"#### Evidence bundle (prepared by orchestrator)\n{evidence_text.strip() or '(empty)'}\n\n"
        f"#### Serialized `data` (truncated)\n```json\n{data_json}\n```"
    )
    return RESEARCH_REPORT_PROMPT.format(
        prompt_role=profile.prompt_role,
        research_focus=profile.research_focus,
        case_and_evidence=case_and_evidence[:150000],
    )


def _fallback_report_text(profile: ResearchAgentProfile, evidence_text: str) -> str:
    ev = evidence_text.strip()
    thin = len(ev) < 40
    ev_note = (
        "The evidence bundle is **thin or empty**; judgments below are explicitly evidence-limited."
        if thin
        else "The following draws only on patterns explicitly visible in the evidence bundle (no web search)."
    )
    return f"""## 1. Key judgment
From a **{profile.title}** perspective, the case requires structured follow-up once higher-quality domain signals are available. {ev_note}

## 2. Supporting evidence
Evidence excerpt (trimmed for the brief): 
```
{ev[:3500] or "(no text supplied)"}
```

## 3. Risks and uncertainties
Domain-specific uncertainty is elevated when indicators for {profile.research_focus} are sparse or ambiguous. Cross-domain spillovers are not inferred here.

## 4. What the chief coordinator should watch
- Evidence freshness and coverage for **{profile.research_focus}**.
- Conflicting narratives across stakeholder groups once richer text is ingested.

## 5. One-sentence recommendation
Treat this track as **provisional** until additional {profile.title.lower()} evidence is collected and reconciled with the MiroFish discussion outputs.
"""


def run_research_agent(
    profile: ResearchAgentProfile,
    case_input: dict[str, Any],
    evidence_text: str,
    model: str = "deepseek-chat",
    *,
    deepseek_mode: str = "auto",
) -> dict[str, Any]:
    """
    Returns a JSON-serializable dict aligned with `ResearchReport`.
    Status: `ok` (LLM), `fallback` (no key / skipped), `failed` (LLM error; body uses fallback text).
    """
    prompt = build_agent_prompt(profile, case_input, evidence_text)
    reporter = DeepSeekReporter(mode=deepseek_mode, model=model)
    api_key = reporter._resolve_api_key()

    if deepseek_mode == "off" or not api_key or deepseek_mode not in {"auto", "live"}:
        text = _fallback_report_text(profile, evidence_text)
        return {
            "agent_id": profile.agent_id,
            "display_name": profile.display_name,
            "title": profile.title,
            "research_focus": profile.research_focus,
            "status": "fallback",
            "report_text": text,
            "errors": [],
        }

    try:
        body = reporter.call_chat_completion(system=_RESEARCH_SYSTEM, user=prompt, api_key=api_key)
        return {
            "agent_id": profile.agent_id,
            "display_name": profile.display_name,
            "title": profile.title,
            "research_focus": profile.research_focus,
            "status": "ok",
            "report_text": body,
            "errors": [],
        }
    except Exception as exc:  # noqa: BLE001
        fb = _fallback_report_text(profile, evidence_text)
        return {
            "agent_id": profile.agent_id,
            "display_name": profile.display_name,
            "title": profile.title,
            "research_focus": profile.research_focus,
            "status": "failed",
            "report_text": fb,
            "errors": [f"{type(exc).__name__}: {exc}"],
        }


def run_all_research_agents(
    case_input: dict[str, Any],
    evidence_text: str,
    model: str = "deepseek-chat",
    *,
    deepseek_mode: str = "auto",
    run_id: str = "",
) -> list[dict[str, Any]]:
    """Run six parallel research briefs (sequential in-process; order stable)."""
    out: list[dict[str, Any]] = []
    for profile in all_research_profiles():
        out.append(
            run_research_agent(
                profile,
                case_input,
                evidence_text,
                model=model,
                deepseek_mode=deepseek_mode,
            )
        )
    return out


def research_run_result_from_dicts(run_id: str, reports: list[dict[str, Any]]) -> ResearchRunResult:
    """Optional helper to materialize dataclasses."""
    errs: list[str] = []
    typed: list[ResearchReport] = []
    for r in reports:
        typed.append(
            ResearchReport(
                agent_id=str(r["agent_id"]),
                display_name=str(r["display_name"]),
                title=str(r["title"]),
                research_focus=str(r["research_focus"]),
                status=str(r["status"]),
                report_text=str(r["report_text"]),
                errors=list(r.get("errors") or []),
            )
        )
        for e in r.get("errors") or []:
            errs.append(f"{r.get('agent_id')}: {e}")
    return ResearchRunResult(run_id=run_id, reports=typed, errors=errs)


def build_evidence_text(case_input: dict[str, Any]) -> str:
    """Flatten case text, narrative, and serialized `data` for research agents."""
    parts: list[str] = []
    t = case_input.get("text")
    if t is not None and str(t).strip():
        parts.append(f"### Case text\n{str(t).strip()}")
    n = case_input.get("narrative")
    if n is not None and str(n).strip():
        parts.append(f"### Narrative\n{str(n).strip()}")
    data = case_input.get("data")
    if isinstance(data, dict):
        parts.append("### Serialized data\n```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```")
    return "\n\n".join(parts) if parts else "(No case text, narrative, or data content supplied.)"
