# Opinion Simulation System (Phase 3)

This package implements a **briefing-first simulation pipeline** for policy/product/culture cases:

`InputCase -> Semantic Evidence -> Group Evolution -> Decision Report`

---

## Scope (Current)

### In scope
- Case-based input and semantic mapping (`InputCase`, `SemanticMapperV2`)
- Structured expert evidence (`acceptance`, `sentiment`, `emotion`, `topic`, `conflict`, `frame`)
- Round-based group evolution with explainable deltas and drivers
- Stable briefing contracts for API/demo/dashboard/report
- Layered reporting (deterministic summary + optional AI expansion)

### Out of scope (for core positioning)
- Treating this package primarily as a high-volume real-time monitoring platform
- Defining success by number of upstream data sources
- Expanding page count without improving briefing clarity

---

## Quick Start

### 1) Run simulation directly
```bash
python -m opinion_sim_system.simulation.runner
```

### 2) Run briefing API
```bash
python -m opinion_sim_system.flask_app
```

### 3) Launch dashboard
```bash
streamlit run opinion_sim_system/visualization/streamlit_app.py
```

### 4) Generate HTML briefing report
```bash
python -m opinion_sim_system.visualization.briefing_report
```

### 5) Run 3-case demo package
```bash
python -m opinion_sim_system.demo.run_demo
```

---

## Four-Layer Dashboard Narrative

The dashboard is organized into briefing-oriented stages:
1. **Conclusion Overview**
2. **Semantic Evidence -> Group Activation**
3. **Group Evolution Mechanism**
4. **Report & Recommendation**

This structure is designed for leadership communication rather than chart proliferation.

---

## Briefing Contract Reference

See: `docs/briefing_contract.md`

Primary emitters/consumers:
- `simulation/runner.py` (phase3 visualization payload)
- `simulation/engine.py` (engine facade, version metadata)
- `reporting/deepseek_reporter.py` + `reporting/report_builder.py`
- `demo/run_demo.py` (phase2b demo envelope)
- `flask_app.py` (`/api/briefing-run` envelope)
- `visualization/*` consumers

Contract-surface note:
- **Runner artifact** (raw simulation output)
- **Briefing API envelope** (`/api/briefing-run`)
- **Demo package envelope** (`demo/run_demo.py`)

These three surfaces are aligned by narrative and shared fields, but they are not strictly identical in every top-level key.

---

## Reporting Model

### Deterministic layer
- Executive summary
- Decision trace
- Stable recommendation slots

### AI expansion layer
- DeepSeek live mode (when API key is configured)
- Fallback deterministic expansion when unavailable

This ensures report stability first, language richness second.

Current rendering note:
- API/demo generate full report envelopes via `DeepSeekReporter`.
- Dashboard and HTML briefing views currently render deterministic view-model outputs by default.

---

## Contract-Oriented Tests

- `tests/test_runner_e2e.py`
- `tests/test_demo_contract.py`
- `tests/test_deepseek_reporter.py`
- `tests/test_engine_api.py`
- `tests/test_flask_briefing_api.py`
- `tests/test_view_model.py`
- `tests/test_briefing_report.py`

Run:
```bash
python -m pytest opinion_sim_system/tests
```

---

## Optional Dependencies

Some visualization and data-collection modules rely on optional packages (for example `streamlit`, `plotly`, `matplotlib`, and selected external connectors). The core briefing pipeline remains usable with deterministic fallbacks where designed.
