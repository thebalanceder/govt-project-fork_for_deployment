# Opinion Simulation System (Phase 1)

> **🔴 NEW: Real-Time Data Collection Available** - Collect real-world data from Reddit, News APIs, and public datasets. See [Real Data Pipeline](#real-data-pipeline) below.

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
6. **Executive Visualization (NEW)**:
   - `visualization/pm_dashboard.py` - Interactive Plotly dashboard
   - `visualization/streamlit_app.py` - Streamlit executive app
   - `visualization/briefing_report.py` - HTML briefing report generator
7. **Real Data Collection (NEW)**:
   - `data_collection/collector.py` - Reddit, NewsAPI, GNews integration
   - `data_collection/run_pipeline.py` - End-to-end real data processing

## Quick Start

### 1. Run Simulation

```bash
python -m opinion_sim_system.simulation.runner
```

Output artifact: `opinion_sim_system/artifacts/phase1/milestone_m1_output.json`

### 2. Generate PM Dashboard (Interactive)

```bash
# Install visualization dependencies
pip install plotly

# Generate static HTML dashboard
python -m opinion_sim_system.visualization.pm_dashboard
```

Output: `opinion_sim_system/artifacts/phase1/pm_dashboard.html`

### 3. Launch Streamlit Executive App (Recommended for PM)

```bash
# Install full visualization stack
pip install streamlit plotly

# Launch interactive dashboard
streamlit run opinion_sim_system/visualization/streamlit_app.py
```

Opens at: `http://localhost:8501`

### 4. Generate Briefing Report (Printable)

```bash
python -m opinion_sim_system.visualization.briefing_report
```

Output: `opinion_sim_system/artifacts/phase1/pm_briefing_report.html`

---

## Visualization Features for Leadership

| Feature | Description | Output |
|---------|-------------|--------|
| **National Sentiment Gauge** | Real-time sentiment index with color-coded status | Dashboard |
| **Population Segment Radar** | 6 archetype group attitudes visualization | Dashboard |
| **Opinion Evolution Charts** | Trend analysis over simulation rounds | Dashboard |
| **Risk Alerts Panel** | Early warning system for negative sentiment | Dashboard + Report |
| **Topic Distribution** | Key issues driving public opinion | Dashboard + Report |
| **Policy Recommendations** | AI-generated action items with priorities | Report |
| **Printable Briefing** | One-page executive summary | HTML/PDF |

---

## Installation

### Minimal (Core Simulation Only)
```bash
pip install numpy
```

### With ML Features
```bash
pip install opinion-sim-system[semantic]
# or
pip install sentence-transformers transformers bertopic
```

### With Visualization (For PM Dashboard)
```bash
pip install opinion-sim-system[viz]
# or
pip install plotly matplotlib streamlit
```

### Full Installation (Recommended)
```bash
pip install opinion-sim-system[all]
```

---

## Real Data Pipeline

### Collect Real-World Data for PM Dashboard

This system now supports **live data collection** from free APIs:

| Source | What You Get | Free Tier |
|--------|--------------|-----------|
| **Reddit** | Public discussions, real-time sentiment | 60 req/min |
| **NewsAPI** | News articles from 70,000+ sources | 100 req/day |
| **GNews** | Global news coverage | 100 req/day |
| **Public Datasets** | Pre-collected sentiment data | Unlimited |

### Quick Setup (5 minutes)

**1. Get API Keys:**
- Reddit: https://www.reddit.com/prefs/apps (create "script" app)
- NewsAPI: https://newsapi.org/register
- GNews: https://gnews.io/

**2. Configure Environment:**
```bash
cd opinion_sim_system
cp .env.example .env
# Edit .env and add your API keys
```

**3. Install Data Dependencies:**
```bash
pip install opinion-sim-system[data]
```

**4. Run Data Collection:**
```bash
python -m opinion_sim_system.data_collection.run_pipeline
```

### Output

Generates real-time dashboards:
- `artifacts/phase1/pm_dashboard_real.html` - Interactive dashboard
- `artifacts/phase1/pm_briefing_real.html` - Printable briefing
- `artifacts/phase1/real_data_analysis.json` - Analysis data

### Detailed Setup Guide

See `data_collection/SETUP.md` for complete instructions.

---

## Backend Behavior (Optional Dependencies)

The system prefers these external backends when installed:

- Embedding: `sentence-transformers`
- Sentiment: `transformers` pipeline
- Topic: `BERTopic`

When these dependencies are unavailable, Phase 1 still runs offline with deterministic fallbacks:

- Embedding fallback: hash-based normalized vectors
- Sentiment fallback: lexicon-based scorer
- Topic fallback: keyword-based topic assignment

---

## For Prime Minister's Office

### Quick Workflow

1. **Run Simulation**: `python -m opinion_sim_system.simulation.runner`
2. **Launch Dashboard**: `streamlit run opinion_sim_system/visualization/streamlit_app.py`
3. **Generate Report**: Click "Print Report" in dashboard or run `python -m opinion_sim_system.visualization.briefing_report`

### Key Metrics Explained

| Metric | Range | Interpretation |
|--------|-------|----------------|
| National Sentiment | -1 to 1 | >0.6 Positive, 0.4-0.6 Caution, <0.4 Critical |
| Segment Attitudes | -1 to 1 | Per-population-group satisfaction |
| Risk Alerts | Count | Number of issues requiring attention |

### Security Classification

Reports are marked `OFFICIAL USE ONLY` by default. Modify in `briefing_report.py` if needed.

---

## Test

```bash
python -m pytest opinion_sim_system/tests
```

---

## Output Artifacts

| File | Description |
|------|-------------|
| `milestone_m1_output.json` | Raw simulation data |
| `pm_dashboard.html` | Interactive executive dashboard |
| `pm_briefing_report.html` | Printable one-page briefing |
