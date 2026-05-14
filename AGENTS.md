# Agent roles and orchestration contract (`govt-project`)

This repository combines **(A) a deterministic Python orchestration layer** and **(B) human / external coding-agent conventions** (OpenCode, Claude Code, Codex, Cursor) so work stays bounded and names stay stable.

## Chief briefing coordinator

| `agent_id` | Display name | Role |
|------------|--------------|------|
| `chief_briefing_coordinator` | **Dr. Helena Marlowe** — Chief Briefing Coordinator | Decomposes a case into topic tracks, dispatches work, tracks execution, aggregates MiroFish outputs, and writes the final briefing artifacts. **Does not replace** `MiroFishDiscussion`; it wraps it. |

**Background (persona):** Senior evidence-to-decision coordinator: expert task decomposition, assignment to domain agents, progress tracking, conflict surfacing, and final decision brief delivery.

**Code:** `opinion_sim_system/orchestrator/` (`run_orchestrated_case`, `build_task_graph`, `chief_profile.py`).

## Domain experts (MiroFish panel)

Canonical names and IDs are defined in code (`opinion_sim_system/agents/six_agents.py`) and mirrored in `agents.manifest.json`. **Do not rename** these experts in docs, logs, or reports without updating the Python source first.

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

1. **Respect boundaries:** Simulation / discussion logic lives under `opinion_sim_system/simulation/`, `opinion_sim_system/mirofish/`, and `opinion_sim_system/agents/`. Orchestration and run artifacts live under `opinion_sim_system/orchestrator/` and `artifacts/orchestrator_runs/`.
2. **Naming:** Use `agent_id` in JSON traces and machine configs; use **display names** in Markdown/HTML briefings and user-facing copy.
3. **Determinism first:** Phase-1 orchestration is deterministic. Optional DeepSeek expansion uses `DEEPSEEK_API_KEY` when present (`DeepSeekReporter.expand_orchestrator_briefing`); it must not change planning or MiroFish math.
4. **Artifacts per run:** `artifacts/orchestrator_runs/<run_id>/` contains `orchestration_trace.json`, `briefing_report.md`, `briefing_report.html`, and `agent_timeline.json`.
5. **CLI entrypoint:** `python -m opinion_sim_system.orchestrator --case opinion_sim_system/orchestrator/sample_case.json`

## Task graph (deterministic)

1. Ingest / validate case payload (`data` dict required for MiroFish).  
2. Plan topics (`economic`, `political`, `cultural` — subset via `topic` or `topics` on the case).  
3. For each topic: run `MiroFishDiscussion.run_discussion`.  
4. Synthesize conflicts, risks, and final recommendation (rule-based).  
5. Emit artifacts + optional DeepSeek narrative expansion.

## When to ask the human

- Changing any of the six domain experts’ **display names** or `agent_id` keys.  
- Replacing `MiroFishDiscussion` internals vs. wrapping them.  
- Introducing LLM-based **planning** (non-deterministic chief) — out of scope for phase 1.
