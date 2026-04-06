# Briefing Contract Specification

## Purpose

Define a stable output contract for the case-based briefing pipeline so API, demo, dashboard, and report layers can evolve without contract drift.

This spec distinguishes **three emitted surfaces**:
1. Runner artifact (raw simulation output)
2. Briefing API envelope (`/api/briefing-run`)
3. Demo package envelope (`demo/run_demo.py`)

They follow one storyline but are not strictly identical at every top-level key.

---

## Canonical Flow

`InputCase -> Semantic Evidence -> Group Evolution -> Report`

---

## Five-Layer Output Model

The five-layer model is a **logical model** shared across surfaces; each surface may project fields differently.

## 1) Input Layer

Required fields:
- `text: str`
- `target: str`
- `domain: "policy" | "product" | "culture"`

Used by:
- `simulation/runner.py` (raw input uses `product_description`, `n_comments`, `target`, `domain`)
- `flask_app.py:/api/briefing-run`
- `demo/run_demo.py`

## 2) Semantic Evidence Layer

Core object:
- `semantic_evidence`

Surface note:
- Demo envelope currently emits `model_evidence` naming at case level.

Expected expert keys:
- `acceptance`
- `sentiment`
- `emotion`
- `topic`
- `conflict`
- `frame`

Plus fusion trace payloads where available.

## 3) Group Activation & Evolution Layer

Core object:
- `simulation_result`

Surface note:
- Runner artifact exposes evolution fields mainly at top-level (`initial_attitudes`, `trajectories`, `visualization_payload`, etc.).
- API/demo expose normalized `simulation_result` objects.

Core fields (API/demo stable subset):
- `initial_attitudes`
- `trajectories`
- `overall_final`
- `dispersion`
- `top_groups`
- `final_group_attitudes`
- `rounds`
- `visualization_payload`

`visualization_payload` (phase3):
- `schema_version: "phase3.v1"`
- `round_count`
- `rounds[]` with per-round deltas/drivers/reasons
- `divergence_summary`
- `driver_summary`
- `provenance_links`

Clarification:
- `simulation_result.rounds` is a count.
- Detailed per-round entries are under `visualization_payload.rounds[]`.

## 4) Executive View Layer

Top-level view fields (briefing API/dashboard consumers):
- `executive_overview`
- `evidence_activation`
- `evolution_highlights`
- `report_recommendation`

These are generated from deterministic report/view builders and should remain additive.

Surface note:
- Briefing API emits these fields directly.
- Dashboard/HTML report commonly derive them from deterministic builders.

## 5) Reporting Layer

Core objects:
- `report`
- `report_text`

`report` stable keys:
- `schema_version` (`phase2b.v1` at current report envelope level)
- `status`
- `provider`
- `mode`
- `text`
- `executive_summary`
- `expanded_analysis`
- `decision_trace`
- `meta`
- `errors`

`report_text` should mirror `report.text`.

Surface note:
- API/demo use `DeepSeekReporter` envelope directly.
- Deterministic view-model rendering may use fallback expansion text in dashboard/report views.

---

## Versioning Notes

- Report envelope currently uses `phase2b.v1`.
- Visualization payload uses `phase3.v1`.
- Keep changes additive unless explicitly version-bumped.

---

## Contract Emitters (Key Files)

- `simulation/runner.py`
- `simulation/engine.py`
- `reporting/deepseek_reporter.py`
- `reporting/report_builder.py`
- `demo/run_demo.py`
- `flask_app.py` (`/api/briefing-run`)

## Contract Consumers (Key Files)

- `visualization/streamlit_app.py`
- `visualization/briefing_report.py`
- `visualization/pm_dashboard.py`
- `tests/test_runner_e2e.py`
- `tests/test_demo_contract.py`
- `tests/test_deepseek_reporter.py`
- `tests/test_engine_api.py`
- `tests/test_flask_briefing_api.py`
- `tests/test_view_model.py`
- `tests/test_briefing_report.py`

---

## Backward-Compatibility Rules

1. Do not remove legacy keys used by existing tests and visualization consumers.
2. New fields should be additive and documented in this file.
3. Keep deterministic summary fields stable (`conclusion_line`, four-block summary slots).
4. Degraded AI mode must preserve envelope shape.

---

## JSON Examples by Surface

## A) Runner Artifact (raw simulation output)

```json
{
  "input": {
    "product_description": "A fairness-focused policy proposal.",
    "n_comments": 3,
    "target": "city service policy",
    "domain": "policy"
  },
  "initial_attitudes": {},
  "trajectories": [],
  "semantic_evidence": {},
  "visualization_payload": {
    "schema_version": "phase3.v1",
    "round_count": 5,
    "rounds": [],
    "divergence_summary": {},
    "driver_summary": {},
    "provenance_links": {}
  }
}
```

## B) Briefing API Envelope (`/api/briefing-run`)

```json
{
  "success": true,
  "schema_version": "phase2b.v1",
  "input": {
    "text": "A fairness-focused policy proposal.",
    "target": "city service policy",
    "domain": "policy"
  },
  "semantic_evidence": {},
  "simulation_result": {
    "initial_attitudes": {},
    "trajectories": [],
    "overall_final": 0.0,
    "dispersion": 0.0,
    "top_groups": [],
    "final_group_attitudes": {},
    "rounds": 5,
    "visualization_payload": {
      "schema_version": "phase3.v1"
    }
  },
  "executive_overview": {},
  "evidence_activation": [],
  "evolution_highlights": [],
  "report_recommendation": {},
  "report": {
    "schema_version": "phase2b.v1",
    "status": "ok",
    "provider": "deepseek",
    "mode": "fallback",
    "text": "...",
    "executive_summary": {},
    "expanded_analysis": "...",
    "decision_trace": {},
    "meta": {},
    "errors": []
  },
  "report_text": "..."
}
```

## C) Demo Package Envelope (`demo/run_demo.py`)

```json
{
  "schema_version": "phase2b.v1",
  "demo": "phase2b",
  "generated_by": {
    "entrypoint": "run_demo",
    "engine": "run_attitude_engine"
  },
  "cases": [
    {
      "case": "policy_case",
      "title": "Tax Reduction Policy Acceptance Simulation",
      "input": {
        "text": "...",
        "target": "...",
        "domain": "policy"
      },
      "model_evidence": {},
      "simulation_result": {
        "initial_attitudes": {},
        "trajectories": [],
        "overall_final": 0.0,
        "dispersion": 0.0,
        "top_groups": [],
        "final_group_attitudes": {},
        "rounds": 5,
        "visualization_payload": {
          "schema_version": "phase3.v1"
        }
      },
      "report": {
        "schema_version": "phase2b.v1"
      },
      "report_text": "..."
    }
  ],
  "artifact_path": ".../demo_output.json"
}
```

Notes:
- API surface uses `semantic_evidence` naming.
- Demo surface currently uses `model_evidence` naming.
- `simulation_result.rounds` is a count, while detailed round entries live in `visualization_payload.rounds[]`.
