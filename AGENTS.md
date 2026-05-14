# Agent roles and orchestration contract (`govt-project`)

This repository combines **(A) a deterministic Python orchestration layer** and **(B) human / external coding-agent conventions** (OpenCode, Claude Code, Codex, Cursor) so work stays bounded and names stay stable.

## Chief briefing coordinator

| `agent_id` | Display name | Role |
|------------|--------------|------|
| `chief_briefing_coordinator` | **Dr. Helena Marlowe** — Chief Briefing Coordinator | Decomposes a case into topic tracks, dispatches pre-MiroFish research briefings and MiroFish discussion work, tracks execution, aggregates outputs, and writes the final decision artifacts. **Does not replace** `MiroFishDiscussion`; it wraps it. |

**Background (persona):** Senior evidence-to-decision coordinator: expert task decomposition, assignment to domain agents, progress tracking, conflict surfacing, and final decision brief delivery.

**Code:** `opinion_sim_system/orchestrator/` (`run_orchestrated_case`, `build_task_graph`, `chief_profile.py`).

## Domain experts (MiroFish panel)

Canonical names and IDs are defined in code (`opinion_sim_system/agents/six_agents.py`) and mirrored in `agents.manifest.json`. **Do not rename** these experts in docs, logs, or reports without updating the Python source first.

## Research report agents (pre-MiroFish)

The same six identities appear again as **research briefing personas** in `opinion_sim_system/research_agents/profiles.py`. They generate structured expert memos from the case + evidence bundle **before** the MiroFish engine runs. Phase 1 uses **no real web search**; outputs are DeepSeek-assisted when `DEEPSEEK_API_KEY` is present, otherwise **deterministic role-specific fallbacks**. The chief coordinator records their work in `agent_timeline.json` (`research_assigned`, `research_working`, `research_completed` / `research_failed`) and merges reports into `briefing_report.md` / `.html` alongside existing simulation sections.

| `agent_id` | Display name (as in UI / reports) |
|------------|-----------------------------------|
| `economist_agent` | Dr. Lim Wei Chen |
| `policy_agent` | Datin Sri Aisha binti Abdullah |
| `business_agent` | Encik Razak bin Ibrahim |
| `sociologist_agent` | Dr. Muthu a/l Krishnan |
| `ir_agent` | Ms. Wong Li Ming |
| `public_agent` | Ahmad bin Hassan |

**Engine:** `opinion_sim_system/mirofish/discussion.py` — class `MiroFishDiscussion` (not replaced by the orchestrator).

## External coding agents — how to work here

1. **Respect boundaries:** Simulation / discussion logic lives under `opinion_sim_system/simulation/`, `opinion_sim_system/mirofish/`, and `opinion_sim_system/agents/`. Pre-MiroFish research briefs live in `opinion_sim_system/research_agents/`. Orchestration and run artifacts live under `opinion_sim_system/orchestrator/` and `artifacts/orchestrator_runs/`.
2. **Naming:** Use `agent_id` in JSON traces and machine configs; use **display names** in Markdown/HTML briefings and user-facing copy.
3. **Determinism first:** Phase-1 orchestration is deterministic. Optional DeepSeek assists **research briefs** (`opinion_sim_system/research_agents/researcher.py`) and the **final narrative expansion** (`DeepSeekReporter.expand_orchestrator_briefing`); neither may change MiroFish numerical behavior.
4. **Artifacts per run:** `artifacts/orchestrator_runs/<run_id>/` contains `orchestration_trace.json`, `agent_timeline.json`, `research_reports.json`, `research_reports.md`, `briefing_report.md`, and `briefing_report.html`.
5. **CLI entrypoint:** `python -m opinion_sim_system.orchestrator --case opinion_sim_system/orchestrator/sample_case.json`
6. **HTTP entrypoint:** `POST /api/orchestrator-run` on the Flask app (same server as `/api/briefing-run`).

## Task graph (deterministic)

1. Ingest / validate case payload (`data` dict required for MiroFish).  
2. Plan topics (`economic`, `political`, `cultural` — subset via `topic` or `topics` on the case).  
3. **Research panel:** six expert research briefs from case + evidence (optional DeepSeek; else fallback).  
4. For each topic: run `MiroFishDiscussion.run_discussion`.  
5. Synthesize conflicts, risks, and final recommendation (rule-based).  
6. Emit artifacts + optional DeepSeek narrative expansion on the full briefing.

## When to ask the human

- Changing any of the six domain experts’ **display names** or `agent_id` keys.  
- Replacing `MiroFishDiscussion` internals vs. wrapping them.  
- Introducing LLM-based **planning** (non-deterministic chief) — out of scope for phase 1.
