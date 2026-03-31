# Opinion Simulation System (Phase 1 / 1.1 / 1.2 / 1.3)

This directory implements the `phase1` series scope defined in `D:\gov-project\develop-phase\phase1.json`.

## Scope Delivered

1. Data scaffold and sample product comments
2. Semantic modules:
   - `models/embedding/embedder.py`
   - `models/sentiment/sentiment_model.py`
   - `models/topic/topic_model.py`
3. Archetype modules:
   - `archetypes/profiles.py`
   - `archetypes/clustering.py`
4. Simulation minimal rules:
   - `simulation/update_rules.py`
   - `simulation/network.py`
5. Orchestration and JSON output:
   - `simulation/runner.py`

## Phase 1.1 Delivered (Semantic Closure Reconstruction)

- Unified state contract in `models/semantic_state.py`
- Semantic compression mapper in `models/semantic_mapper.py`
- Continuity / decoupling / cross-batch checks in `experiments/semantic_checks.py`
- Runner integration: `SemanticState` is now the dynamics input interface

## Phase 1.2 Delivered (Three-loop six-stage plan in current codebase)

- Stage 1 (state unification): `SemanticState` integrated end-to-end
- Stage 2 (heterogeneous update): `simulation/update_rules.py` adds
  `f(agent_profile, agent_state, neighbors_state, semantic_state)` with step-bound constraints
- Stage 3 (stability/emergence): `simulation/runner.py` emits dynamics convergence/volatility/dispersion metrics
- Stage 4 (explainability): per-round per-group attribution is persisted in trajectory records
- Stage 5 (cross-task consistency): runner performs policy/product/support task configuration checks
- Stage 6 (API/frontend packaging): runner emits `api_frontend_bundle` chain metadata for integration

## Phase 1.3 Delivered (Semantic → Group Attitude Engine)

- Canonical semantic interface remains `SemanticState` (sentiment/stance/topic/embedding)
- Canonical mapping interface remains `SemanticMapper`
- Heterogeneous group update via `heterogeneous_update_attitude`
- Per-round attribution includes phase1.3 categories: `self/semantic/neighbor/noise`
- Runner outputs dynamics indicators: `convergence/volatility/dispersion`
- Runner validates cross-task consistency across `policy/product/support`
- Engine facade provided in `simulation/engine.py` (`run_attitude_engine`, `AttitudeEngine`)
- `api_frontend_bundle.api_version` is aligned to `phase1.3`

## Quick Start

```bash
python -m opinion_sim_system.simulation.runner
```

Or use the phase1.3 engine facade:

```bash
python -c "from opinion_sim_system.simulation.engine import run_attitude_engine; run_attitude_engine('A reliable product')"
```

Output artifact:

`opinion_sim_system/artifacts/phase1/milestone_m1_output.json`

## Backend Behavior (Optional Dependencies)

The system prefers these external backends when installed:

- Embedding: `sentence-transformers`
- Sentiment: `transformers` pipeline
- Topic: `BERTopic`

When these dependencies are unavailable, Phase 1 still runs offline with deterministic fallbacks:

- Embedding fallback: hash-based normalized vectors
- Sentiment fallback: lexicon-based scorer
- Topic fallback: keyword-based topic assignment

## Test

```bash
python -m pytest opinion_sim_system/tests
```
