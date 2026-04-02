# 🇲🇾 CSPOPS Malaysia - Complete Rewrite

## Citizen Sentiment & Public Opinion Perception System

### Multi-Agent AI Discussion & Forecasting Platform

---

## 🎯 New Architecture

### Three Core Topics:
1. **📊 Economic** - GDP, inflation, employment, trade
2. **🏛️ Political** - Policies, governance, international relations
3. **🎭 Cultural** - Social cohesion, identity, values

### Six Expert AI Agents:
Each agent uses Hugging Face pre-trained models for analysis

| Agent | Role | Perspective | HF Model |
|-------|------|-------------|----------|
| **Dr. Lim** | Chief Economist | Economic growth, stability | `finbert` |
| **Datin Sri Aisha** | Policy Advisor | Governance, public welfare | `bert-government` |
| **Encik Razak** | Business Leader | Industry, investment | `finbert` |
| **Dr. Muthu** | Sociologist | Social cohesion, culture | `roberta-social` |
| **Ms. Wong** | International Relations | Geopolitics, trade | `xlm-roberta` |
| **Ahmad** | Public Representative | Citizen concerns | `distilbert-sentiment` |

---

## 🔄 MiroFish Opinion Evolution

### How It Works:
```
1. Data Collection (Real-time news, social media)
   ↓
2. Individual Agent Analysis (Each agent analyzes from their perspective)
   ↓
3. Multi-Agent Discussion (MiroFish-style debate)
   ↓
4. Opinion Evolution (Agents influence each other)
   ↓
5. Consensus Building (Weighted aggregation)
   ↓
6. Final Forecast (Per topic + overall)
```

---

## 📊 Output Structure

### For Each Topic (Economic, Political, Cultural):

**Individual Agent Forecasts:**
```json
{
  "topic": "economic",
  "agent": "Dr. Lim (Economist)",
  "current_sentiment": 0.65,
  "forecast_7d": 0.68,
  "forecast_30d": 0.72,
  "confidence": 0.85,
  "key_factors": ["GDP growth", "Inflation control", "Employment"],
  "reasoning": "GDP expected to grow 4.5-5.5%..."
}
```

**MiroFish Evolution:**
```json
{
  "topic": "economic",
  "round_0": {
    "Dr. Lim": 0.65,
    "Datin Sri Aisha": 0.58,
    "Encik Razak": 0.70,
    ...
  },
  "round_1": {
    "Dr. Lim": 0.66,
    "Datin Sri Aisha": 0.60,
    ...
  },
  "consensus": 0.68,
  "convergence_rate": 0.85
}
```

**Final Analysis:**
```json
{
  "economic": {
    "sentiment": 0.68,
    "trend": "positive",
    "confidence": 0.85,
    "forecast": "GDP growth expected to accelerate..."
  },
  "political": {
    "sentiment": 0.55,
    "trend": "stable",
    "confidence": 0.78,
    "forecast": "Policy continuity expected..."
  },
  "cultural": {
    "sentiment": 0.72,
    "trend": "positive",
    "confidence": 0.82,
    "forecast": "Social cohesion improving..."
  }
}
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│              Data Collection Layer               │
│  • News Crawler (Economic, Political, Cultural) │
│  • Social Media (Reddit, Twitter, Telegram)     │
│  • Government APIs                               │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           Individual Agent Analysis              │
│  ┌────────────────────────────────────────┐    │
│  │  Dr. Lim (Economist)                   │    │
│  │  Model: finbert                        │    │
│  │  Focus: GDP, inflation, employment     │    │
│  └────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────┐    │
│  │  Datin Sri Aisha (Policy Advisor)      │    │
│  │  Model: bert-government                │    │
│  │  Focus: Governance, public welfare     │    │
│  └────────────────────────────────────────┘    │
│  ... (6 agents total)                          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│          MiroFish Multi-Agent Discussion         │
│  • Round 1: Initial positions                    │
│  • Round 2: Agents respond to each other         │
│  • Round 3: Convergence toward consensus         │
│  • Influence weights based on expertise          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         Forecasting & Explanation                │
│  • 7-day forecast per topic                      │
│  • 30-day forecast per topic                     │
│  • Confidence scores                             │
│  • Natural language explanations                 │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            Web Dashboard                         │
│  • Agent discussion visualization                │
│  • Opinion evolution charts                      │
│  • Forecast comparisons                          │
│  • Interactive Q&A                               │
└─────────────────────────────────────────────────┘
```

---

## 🤖 Agent Definitions

### 1. Dr. Lim Wei Chen - Chief Economist
**Background:** Former Bank Negara economist, 20+ years experience
**HF Model:** `prosusai/finbert`
**Perspective:** Economic stability, growth, inflation control
**Influence Weight:** 1.2x (high on economic topics)

### 2. Datin Sri Aisha binti Abdullah - Policy Advisor
**Background:** Former minister, policy think tank director
**HF Model:** `joeddav/distilbert-base-uncased-go-emotions-student`
**Perspective:** Public welfare, governance effectiveness
**Influence Weight:** 1.1x (high on political topics)

### 3. Encik Razak bin Ibrahim - Business Leader
**Background:** CEO of multinational corporation, FMM council member
**HF Model:** `prosusai/finbert`
**Perspective:** Industry growth, investment climate, competitiveness
**Influence Weight:** 1.1x (high on economic topics)

### 4. Dr. Muthu a/l Krishnan - Sociologist
**Background:** UM sociology professor, social researcher
**HF Model:** `cardiffnlp/twitter-roberta-base-sentiment`
**Perspective:** Social cohesion, cultural identity, inequality
**Influence Weight:** 1.2x (high on cultural topics)

### 5. Ms. Wong Li Ming - International Relations Expert
**Background:** Former diplomat, ASEAN specialist
**HF Model:** `xlm-roberta-base`
**Perspective:** Geopolitics, trade relations, regional stability
**Influence Weight:** 1.0x (balanced)

### 6. Ahmad bin Hassan - Public Representative
**Background:** Community leader, grassroots organizer
**HF Model:** `distilbert-base-uncased-finetuned-sst-2-english`
**Perspective:** Citizen concerns, cost of living, quality of life
**Influence Weight:** 1.1x (high on social topics)

---

## 🎯 MiroFish Discussion Flow

### Example: Economic Topic Discussion

**Round 0 - Initial Analysis:**
```
Dr. Lim: GDP growth outlook positive at 0.72 sentiment
Encik Razak: Business confidence high at 0.68 sentiment
Datin Sri Aisha: Policy support adequate at 0.60 sentiment
...
Average: 0.65
```

**Round 1 - Cross-Discussion:**
```
Dr. Lim responds to Encik Razak:
"Business confidence aligns with GDP indicators. 
Updating sentiment to 0.70 based on investment data."

Datin Sri Aisha responds to Dr. Lim:
"Policy measures support growth but inequality concerns remain.
Maintaining 0.60 sentiment."
...
Average: 0.67
```

**Round 2 - Convergence:**
```
After 3 rounds of discussion:
Consensus: 0.68
Convergence: 85%
Confidence: 0.82
```

**Final Forecast:**
```
Economic Outlook: Positive (0.68)
7-day forecast: 0.70 (improving)
30-day forecast: 0.72 (sustained growth)
Key drivers: GDP growth, investment, policy support
Risks: Inflation pressure, global uncertainty
```

---

## 📁 New File Structure

```
opinion_sim_system/
├── agents/
│   ├── __init__.py
│   ├── agent_base.py              # Base agent class
│   ├── economist_agent.py         # Dr. Lim
│   ├── policy_agent.py            # Datin Sri Aisha
│   ├── business_agent.py          # Encik Razak
│   ├── sociologist_agent.py       # Dr. Muthu
│   ├── ir_agent.py                # Ms. Wong
│   └── public_agent.py            # Ahmad
├── mirofish/
│   ├── __init__.py
│   ├── discussion.py              # Multi-agent discussion
│   ├── evolution.py               # Opinion evolution
│   └── consensus.py               # Consensus building
├── forecasting/
│   ├── __init__.py
│   ├── predictor.py               # Forecasting models
│   └── explanation.py             # NLG explanations
├── data_collection/
│   ├── __init__.py
│   ├── crawler.py                 # News crawler (3 topics)
│   └── apis.py                    # API integrations
├── web_app/
│   ├── __init__.py
│   ├── app.py                     # Flask/FastAPI backend
│   ├── templates/
│   │   └── index.html             # Dashboard
│   └── static/
│       ├── js/
│       │   ├── dashboard.js
│       │   └── discussion_viz.js
│       └── css/
│           └── style.css
└── config/
    ├── agents.yaml                # Agent configurations
    └── topics.yaml                # Topic definitions
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install transformers torch
pip install flask plotly pandas numpy
pip install requests beautifulsoup4
```

### 2. Run Data Crawler
```bash
python3 crawl_malaysian_news.py
# Collects economic, political, cultural news
```

### 3. Start Multi-Agent Discussion
```bash
python3 -m opinion_sim_system.mirofish.discussion
# 6 agents discuss, evolve opinions, generate forecasts
```

### 4. Launch Dashboard
```bash
python3 -m opinion_sim_system.web_app.app
# Open http://localhost:5000
```

---

## 📊 Dashboard Features

### 1. Agent Discussion View
- Live discussion transcript
- Agent sentiment positions
- Opinion evolution over rounds

### 2. Forecast Comparison
- 6 agent forecasts per topic
- Consensus forecast
- Confidence intervals

### 3. Topic Breakdown
- Economic sentiment & forecast
- Political sentiment & forecast
- Cultural sentiment & forecast

### 4. Interactive Q&A
- Ask questions to specific agents
- Get agent perspectives
- Compare viewpoints

---

## ✅ Expected Output

### Console Output:
```
🇲🇾 CSPOPS Malaysia - Multi-Agent AI Discussion
================================================

📊 Topic: Economic
─────────────────────────────────────────────────
Dr. Lim (Economist): Initial sentiment 0.72 (positive)
Encik Razak (Business): Initial sentiment 0.68 (positive)
Datin Sri Aisha (Policy): Initial sentiment 0.60 (neutral)
...

🔄 MiroFish Discussion - Round 1
─────────────────────────────────────────────────
Dr. Lim responds to Encik Razak:
"Business confidence aligns with GDP indicators..."
Updated sentiment: 0.70

🔄 MiroFish Discussion - Round 2
─────────────────────────────────────────────────
Datin Sri Aisha responds to Dr. Lim:
"Policy measures support growth but..."
Updated sentiment: 0.62

✅ Consensus Reached
─────────────────────────────────────────────────
Economic Sentiment: 0.68 (positive)
Convergence: 85%
Confidence: 0.82

📈 Forecast
─────────────────────────────────────────────────
7-day: 0.70 (improving)
30-day: 0.72 (sustained growth)
Key drivers: GDP growth, investment, policy support
```

---

## 🎯 Key Innovations

1. **Multi-Agent AI** - 6 expert perspectives, not single model
2. **MiroFish Methodology** - Opinion evolution through discussion
3. **Topic-Specific** - Economic, political, cultural (focused)
4. **Explainable** - Each agent provides reasoning
5. **Forecasting** - 7-day and 30-day predictions
6. **Malaysian Context** - Local experts, local issues

---

**This is a complete rewrite with 6 AI agents, MiroFish discussion, and 3-topic focus!** 🇲🇾✨

Ready to implement? I can start with the agent definitions and MiroFish discussion engine.
