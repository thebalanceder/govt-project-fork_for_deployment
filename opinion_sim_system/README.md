# Opinion Simulation System (Phase 1)

This directory implements the Phase 1 scope defined in `D:\gov-project\develop-phase.json`.

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

## Quick Start

```bash
python -m opinion_sim_system.simulation.runner
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
