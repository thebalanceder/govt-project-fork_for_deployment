# CSPOPS — Evidence-to-Decision Briefing System

This repository is now positioned as a **case-based simulation and briefing system**:

`InputCase -> Semantic Evidence -> Group Evolution -> Decision Brief`

The project is optimized for **stable reporting and decision communication**, not for broad real-time monitoring claims.

---

## Product Positioning (Unified)

## Legacy-to-Current Narrative Mapping

| Legacy wording | Current wording |
|---|---|
| Real-time monitoring platform | Case-based briefing simulation system |
| 170+ sources as core value | Evidence quality + explainable simulation contract |
| 8-tab dashboard expansion | Four-layer briefing narrative (Conclusion/Evidence/Mechanism/Recommendation) |
| AI Panel as standalone feature | Layered report system (deterministic summary + AI expansion) |
| Broad monitoring success criteria | Stable briefing output and decision communication quality |

### What this system does
- Accepts a case input (`text`, `target`, `domain`) for policy/product/culture topics.
- Extracts structured semantic evidence (expert signals such as acceptance/conflict/frame).
- Simulates multi-group attitude evolution across rounds.
- Produces deterministic + AI-extended briefing outputs for dashboards and reports.

### What this system does not claim
- No benchmark claim on "170+ real-time sources" as the core product identity.
- No "8-tab monitoring platform" positioning as the primary story.
- No dependency on always-online data collection for core briefing flow.

---

## Architecture Overview

### Core pipeline
1. **Input Layer**
   - `InputCase(text, target, domain)`
2. **Semantic Evidence Layer**
   - `SemanticMapperV2` expert outputs + fusion traces
3. **Group Activation & Evolution Layer**
   - simulation rounds, trajectory deltas, dispersion, dominant drivers
4. **Decision Reporting Layer**
   - deterministic executive summary + optional DeepSeek expansion
5. **Presentation Layer**
   - briefing API, Streamlit dashboard, HTML briefing report

### Key entrypoints
- Briefing API: `POST /api/briefing-run` via `python -m opinion_sim_system.flask_app`
- Demo package: `python -m opinion_sim_system.demo.run_demo`
- Streamlit dashboard: `streamlit run opinion_sim_system/visualization/streamlit_app.py`
- HTML briefing report: `python -m opinion_sim_system.visualization.briefing_report`
- Chief orchestrator (multi-topic MiroFish + run artifacts): `python -m opinion_sim_system.orchestrator --case opinion_sim_system/orchestrator/sample_case.json` — see root `AGENTS.md`

---

## Quick Start

### 1) Install
```bash
pip install -e .
```

### 2) Run API
```bash
python -m opinion_sim_system.flask_app
```

### 3) Call briefing pipeline
```bash
curl -X POST http://localhost:5000/api/briefing-run \
  -H "Content-Type: application/json" \
  -d '{"text":"A fairness-focused policy proposal.","target":"city service policy","domain":"policy"}'
```

### 4) Run fixed 3-case demo package
```bash
python -m opinion_sim_system.demo.run_demo
```

---

## Stable Briefing Contract

See: `opinion_sim_system/docs/briefing_contract.md`

Contract outputs are organized into five logical layers:
- `input`
- `semantic_evidence`
- `simulation_result`
- `executive_overview / evidence_activation / evolution_highlights`
- `report / report_text`

Important: there are currently **three contract surfaces** (runner artifact, briefing API envelope, demo envelope). They share the same storyline but are not byte-identical key-for-key.

---

## Layered Reporting Model

The reporting model is intentionally two-layered:
- **Deterministic layer**: executive summary + decision trace (stable, testable)
- **AI expansion layer**: richer narrative (DeepSeek live/fallback)

This keeps conclusions stable while still enabling richer language for presentations.

Current behavior note:
- API/demo paths use `DeepSeekReporter` envelopes directly.
- Dashboard/HTML report views are currently built from deterministic view-model outputs (with fallback expansion text) unless explicitly fed API/demo report payloads.

---

## Validation & Tests

Key contract checks live in:
- `opinion_sim_system/tests/test_runner_e2e.py`
- `opinion_sim_system/tests/test_demo_contract.py`
- `opinion_sim_system/tests/test_deepseek_reporter.py`
- `opinion_sim_system/tests/test_engine_api.py`
- `opinion_sim_system/tests/test_flask_briefing_api.py`
- `opinion_sim_system/tests/test_view_model.py`

Run:
```bash
python -m pytest opinion_sim_system/tests
```

---

## Note on Legacy Monitoring Modules

The repository still contains legacy/experimental data-collection and monitoring modules.
They are **not** the primary product narrative for this phase.

Current primary narrative and acceptance criteria are centered on:
**case-based briefing, semantic evidence, group evolution, and report outputs.**
