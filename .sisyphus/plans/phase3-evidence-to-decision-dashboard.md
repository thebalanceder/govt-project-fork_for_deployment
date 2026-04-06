# Phase 3: Evidence-to-Decision Dashboard

## Objective
Turn the current semantic evidence → group evolution → reporting chain into a stronger, leadership-ready dashboard/report pipeline without breaking existing Phase 1 / Phase 2B contracts.

## Key decisions
- Scope: `opinion_sim_system` only.
- Demo package: keep the existing 3 fixed cases.
- Compatibility: additive-only contract changes; no removals/renames of current JSON keys.
- Default verification mode: deterministic/fallback.

## Scope
### In
- Richer backend payload for visualization and decision traceability.
- Two-layer report architecture: deterministic executive summary + AI expansion.
- Dashboard/report consumer updates for the richer contract.
- Demo/API compatibility hardening.

### Out
- No new demo cases.
- No major semantic fusion algorithm rewrite.
- No full front-end redesign beyond the existing dashboard/report surfaces.

## Guardrails
- Preserve existing keys used by current tests and dashboards.
- Prefer backend-derived metrics as the single source of truth.
- Keep live AI reporting optional; deterministic path must always work.
- New fields must be documented and present consistently across all rounds/cases.

## Design notes
- Extend `simulation/runner.py` with a visualization-friendly payload that captures per-round deltas, dominant drivers, dispersion, and provenance links.
- Use `models/semantic_fusion.py` as the explainability hub for evidence-to-decision lineage.
- Keep `reporting/deepseek_reporter.py` as the expansion layer while adding a deterministic executive summary layer.
- Update `flask_app.py`, `visualization/pm_dashboard.py`, `visualization/streamlit_app.py`, and `visualization/briefing_report.py` to read the upgraded contract defensively.
- Keep `demo/run_demo.py` on the same 3 cases but elevate the report envelope and case-level narration.

## Tasks

### 1. Define the enhanced evidence-to-decision contract
- **Goal:** Specify the new additive JSON fields for visualization and reporting.
- **Primary files:** `simulation/runner.py`, `models/semantic_fusion.py`, `contracts.py` (if versioning is needed).
- **Additions to define:** `visualization_payload`, `decision_trace`, `decision_confidence`, `driver_summary`, `provenance_links`.
- **Acceptance criteria:**
  - Existing keys remain untouched.
  - New fields are additive and documented.
  - One canonical example payload exists in the plan artifacts.
- **QA scenarios:**
  - Legacy consumer reading old keys only still works.
  - New consumer can read the added decision lineage fields.

### 2. Extend runner output with visualization payload
- **Goal:** Produce round-level metadata that the dashboard can render directly.
- **Primary files:** `simulation/runner.py`, `simulation/engine.py`.
- **Payload requirements:** per-round deltas, dominant driver label, dispersion, group proximity/divergence summary, activation reason bundle.
- **Acceptance criteria:**
  - Every trajectory entry has the new fields.
  - `trajectories` keeps the original keys for compatibility.
  - The engine facade still returns the same top-level contract plus the enriched payload.
- **QA scenarios:**
  - 3-round demo produces deterministic enriched payload.
  - Existing runner tests still pass with additive assertions.

### 3. Build the two-layer reporting flow
- **Goal:** Separate deterministic executive summary from AI expansion.
- **Primary files:** `reporting/deepseek_reporter.py`, new `reporting/report_builder.py` or equivalent helper, and any schema helper needed.
- **Layering:**
  - Layer 1: deterministic summary derived from structured outputs.
  - Layer 2: DeepSeek expansion (live or fallback) that elaborates the summary.
- **Acceptance criteria:**
  - Report envelope always includes structured summary + expansion text.
  - Fallback mode remains deterministic.
  - Live mode remains optional and non-blocking.
- **QA scenarios:**
  - Missing API key returns a stable fallback report.
  - Live mode failure degrades to fallback without breaking the envelope.

### 4. Update dashboard and briefing consumers
- **Goal:** Make the existing views consume the richer contract without losing legacy support.
- **Primary files:** `flask_app.py`, `visualization/pm_dashboard.py`, `visualization/streamlit_app.py`, `visualization/briefing_report.py`.
- **UI focus:** overview, semantic evidence-to-activation, group evolution, report/recommendations.
- **Acceptance criteria:**
  - Views render when new fields are present.
  - Views still render when only legacy fields are present.
  - The briefing output surfaces decision trace and recommendation language.
- **QA scenarios:**
  - Old artifact loads with no errors.
  - Enhanced artifact shows the new sections and metrics.

### 5. Harden the 3-case demo and API envelope
- **Goal:** Keep the demo stable while raising the quality of the emitted narrative and artifact envelope.
- **Primary files:** `demo/run_demo.py`, `demo/contracts.py`, `flask_app.py`.
- **Acceptance criteria:**
  - The 3 fixed cases remain unchanged.
  - Each case produces a richer report envelope.
  - `/api/briefing-run` remains backward-compatible with the new contract.
- **QA scenarios:**
  - All 3 demo cases run end-to-end.
  - API response includes both legacy and enhanced report sections.
  - Report text matches the report object payload.

## Final Verification Wave
- Validate backward compatibility on the existing 3 demo cases.
- Validate `/api/briefing-run` envelope shape and report text parity.
- Validate dashboard/report rendering against legacy and enhanced payloads.
- Confirm deterministic outputs in fallback mode.
