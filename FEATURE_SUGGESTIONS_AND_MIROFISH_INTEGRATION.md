# 🚀 CSPOPS Feature Suggestions & MiroFish Integration Plan

## ✅ NLP Error Fixed

The "Token indices sequence length" error has been resolved by:
1. Adding automatic text truncation before model processing
2. Setting `truncation=True` and `max_length=510` in pipeline initialization
3. Pre-truncating texts to 1600 characters (400 tokens × 4 chars/token)

---

## 📋 Suggested New Features

### 🔥 Priority 1: Core Features

#### 1. **Multi-Agent AI Discussion System** ⭐⭐⭐
**Description**: Integrate the existing 6-agent MiroFish system with real-time data

**Features**:
- Agents analyze collected news/data independently
- Structured debate rounds with opinion evolution
- Consensus building with convergence tracking
- Final forecasts with confidence intervals

**Implementation**:
```python
# In flask_app.py collect endpoint
after data collection:
    from opinion_sim_system.mirofish.discussion import run_all_topics_discussion
    
    # Run discussions for each topic
    discussion_results = run_all_topics_discussion(data_dict)
    
    # Store results for dashboard
    dashboard_data['agent_discussions'] = discussion_results
```

**Dashboard Tab**: "AI Panel Discussion"
- Show 6 agents with their positions
- Visualize opinion evolution over rounds
- Display final consensus and forecasts

---

#### 2. **Real-Time Alert System** ⭐⭐⭐
**Description**: Monitor for critical sentiment changes and trigger alerts

**Features**:
- Threshold-based alerts (sentiment drops below -0.5)
- Trend alerts (rapid negative sentiment increase)
- Crisis detection (spike in fear/anger emotions)
- SMS/Email notifications

**Implementation**:
```python
class AlertMonitor:
    def check_alerts(self, sentiment_data, emotion_data):
        alerts = []
        
        # Critical sentiment drop
        if sentiment_data['compound'] < -0.5:
            alerts.append({
                'type': 'CRITICAL_SENTIMENT',
                'severity': 'high',
                'message': f"Negative sentiment detected: {sentiment_data['compound']:.2f}"
            })
        
        # Anger spike
        if emotion_data.get('anger', 0) > 0.4:
            alerts.append({
                'type': 'ANGER_SPIKE',
                'severity': 'medium',
                'message': f"High anger levels: {emotion_data['anger']:.0%}"
            })
        
        return alerts
```

---

#### 3. **Trend Analysis & Predictions** ⭐⭐⭐
**Description**: Time-series analysis and forecasting

**Features**:
- 7-day and 30-day sentiment forecasts
- Trend detection (rising/falling/stable)
- Seasonal pattern recognition
- ARIMA/Prophet integration

**Visualization**:
- Line charts with forecast cones
- Trend indicators (📈 📉 ➡️)
- Confidence intervals

---

### 🌟 Priority 2: Enhanced Analytics

#### 4. **Demographic Segmentation** ⭐⭐
**Description**: Break down sentiment by demographic groups

**Data Sources**:
- Reddit user flairs (age/location)
- News source demographics
- Survey integration

**Dashboard**:
- Sentiment by age group
- Sentiment by region (state-level for Malaysia)
- Urban vs Rural divide

---

#### 5. **Topic Modeling & Clustering** ⭐⭐
**Description**: Automatic topic discovery from news/social media

**Implementation**:
```python
from bertopic import BERTopic

topic_model = BERTopic(
    language="multilingual",
    nr_topics=10,  # Discover 10 main topics
)

topics, probs = topic_model.fit_transform(all_texts)
```

**Dashboard**:
- Topic cloud visualization
- Topic trend over time
- Sentiment per topic

---

#### 6. **Misinformation Detection** ⭐⭐
**Description**: Flag potentially misleading content

**Features**:
- Credibility scoring
- Source reliability ratings
- Cross-reference with fact-checking APIs
- Clickbait detection

---

#### 7. **Comparative Analysis** ⭐⭐
**Description**: Compare Malaysia with other countries

**Features**:
- Regional sentiment comparison (SG, TH, ID, PH)
- Economic indicator benchmarking
- Policy outcome comparisons

---

### 💎 Priority 3: User Experience

#### 8. **Custom Dashboard Builder** ⭐
**Description**: Let users customize their dashboard

**Features**:
- Drag-and-drop widgets
- Custom metric selection
- Save multiple dashboard configurations
- Role-based views (PM, Minister, Analyst)

---

#### 9. **Report Generator** ⭐
**Description**: Auto-generate PDF/PPT reports

**Templates**:
- Daily Briefing (2 pages)
- Weekly Summary (5 pages)
- Monthly Analysis (10 pages)
- Crisis Report (on-demand)

**Export Formats**: PDF, PowerPoint, Word

---

#### 10. **Mobile App** ⭐
**Description**: iOS/Android app for on-the-go monitoring

**Features**:
- Push notifications for alerts
- Quick sentiment snapshot
- Voice queries ("What's the sentiment today?")
- Offline mode

---

## 🎯 MiroFish 6-Agent Integration

### Current State
You have:
- ✅ 6 Expert Agents implemented in `agents/six_agents.py`
- ✅ MiroFish discussion engine in `mirofish/discussion.py`
- ✅ Test script in `test_multi_agent.py`
- ✅ Real-time data collection in `unified_collector.py`

### Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Flask App                             │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │   Data       │    │   NLP        │    │  MiroFish │  │
│  │   Collection │───▶│   Analysis   │───▶│  Agents  │  │
│  │              │    │              │    │          │  │
│  └──────────────┘    └──────────────┘    └──────────┘  │
│         │                   │                  │        │
│         │                   │                  ▼        │
│         │                   │          ┌────────────┐  │
│         │                   │          │ Discussion │  │
│         │                   │          │  Results   │  │
│         │                   │          └────────────┘  │
│         ▼                   │                  │        │
│  ┌──────────────┐          │                  ▼        │
│  │   Unified    │          │         ┌─────────────┐  │
│  │  Collector   │          │         │ Dashboard   │  │
│  │  (170+ items)│          │         │  Display    │  │
│  └──────────────┘          │         └─────────────┘  │
│                            │                           │
└────────────────────────────┴───────────────────────────┘
```

### Step-by-Step Integration

#### Step 1: Create Data Adapter

Create `opinion_sim_system/integration/data_adapter.py`:

```python
"""
Convert unified collection data to MiroFish format
"""

from typing import Dict, List, Any

class MiroFishDataAdapter:
    """Convert collected data to format expected by MiroFish agents."""
    
    @staticmethod
    def convert_to_agent_format(data: Dict[str, List]) -> Dict[str, Any]:
        """
        Convert unified collector output to MiroFish input format.
        
        Args:
            data: {'economic': [...], 'political': [...], 'cultural': [...]}
            
        Returns:
            Formatted data for agent analysis
        """
        agent_data = {
            'economic': [],
            'political': [],
            'cultural': [],
            'social_media': [],
            'news': []
        }
        
        # Convert each category
        for category in ['economic', 'political', 'cultural']:
            items = data.get(category, [])
            for item in items:
                # Convert DataItem to dict if needed
                if hasattr(item, '__dict__'):
                    item_dict = {
                        'text': item.text,
                        'title': item.title,
                        'source': item.source,
                        'timestamp': item.timestamp.isoformat() if hasattr(item, 'timestamp') else '',
                        'value': item.value if hasattr(item, 'value') else None,
                        'metadata': item.metadata if hasattr(item, 'metadata') else {}
                    }
                else:
                    item_dict = item
                
                agent_data[category].append(item_dict)
                agent_data['news'].append(item_dict)
        
        return agent_data
```

#### Step 2: Update Flask App Integration

In `flask_app.py`, add MiroFish integration to `/api/collect`:

```python
@app.route('/api/collect', methods=['POST'])
def collect_data():
    # ... existing collection code ...
    
    # NEW: Run MiroFish agent discussions
    from opinion_sim_system.integration.data_adapter import MiroFishDataAdapter
    from opinion_sim_system.mirofish.discussion import run_all_topics_discussion
    
    # Convert data format
    adapter = MiroFishDataAdapter()
    agent_data = adapter.convert_to_agent_format(all_data)
    
    # Run discussions
    print("\n🤖 Starting Multi-Agent Discussions...")
    discussion_results = run_all_topics_discussion(agent_data)
    
    # Store results
    dashboard_data['agent_discussions'] = {
        topic: {
            'final_consensus': result.final_consensus,
            'convergence_rate': result.convergence_rate,
            'agent_forecasts': result.agent_forecasts,
            'explanation': result.explanation,
            'rounds': len(result.rounds)
        }
        for topic, result in discussion_results.items()
    }
    
    return jsonify({
        'success': True,
        'summary': summary,
        'agent_discussions_available': True
    })
```

#### Step 3: Add API Endpoint for Agent Results

```python
@app.route('/api/agents')
def get_agent_results():
    """Get multi-agent discussion results."""
    if 'agent_discussions' in dashboard_data:
        return jsonify(dashboard_data['agent_discussions'])
    return jsonify({'error': 'No agent discussions available'}), 404
```

#### Step 4: Create Frontend Tab

Add to `index.html`:

```html
<!-- AI Panel Discussion Tab -->
<section id="agents" class="tab-content">
    <h2><i class="fas fa-robot"></i> AI Panel Discussion</h2>
    
    <!-- Agent Cards -->
    <div class="agent-grid" id="agent-grid"></div>
    
    <!-- Discussion Progress -->
    <div class="discussion-timeline" id="discussion-timeline"></div>
    
    <!-- Consensus Visualization -->
    <div class="consensus-chart" id="consensus-chart"></div>
    
    <!-- Agent Forecasts -->
    <div class="forecast-grid" id="forecast-grid"></div>
</section>
```

#### Step 5: JavaScript for Agent Display

Add to `app.js`:

```javascript
async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE}/api/agents`);
        const data = await response.json();
        
        // Display 6 agents
        const agentGrid = document.getElementById('agent-grid');
        agentGrid.innerHTML = `
            <div class="agent-cards">
                ${Object.entries(data.economic.agent_forecasts).map(([name, forecast]) => `
                    <div class="agent-card">
                        <h4>${name}</h4>
                        <div class="sentiment-badge ${getSentimentClass(forecast.sentiment)}">
                            ${formatSentiment(forecast.sentiment)}
                        </div>
                        <div class="forecast">
                            <div>7-day: ${forecast.forecast_7d.toFixed(2)}</div>
                            <div>30-day: ${forecast.forecast_30d.toFixed(2)}</div>
                        </div>
                        <div class="confidence">
                            Confidence: ${(forecast.confidence * 100).toFixed(0)}%
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        // Show consensus
        updateConsensusChart(data);
        
    } catch (error) {
        console.error('Agent fetch error:', error);
    }
}
```

---

### Dashboard Mockup for AI Agents

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 AI Panel Discussion - Economic Analysis                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Consensus: +0.42 (Positive) ━━━━━━━━━━━━━━━━ 78% Converged│
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Agent Positions                                     │  │
│  │                                                       │  │
│  │  👨‍💼 Dr. Lim (Economist)      +0.65  📈 Optimistic   │  │
│  │  👩‍💼 Datin Aisha (Policy)     +0.42  👍 Positive    │  │
│  │  👨‍💼 Encik Razak (Business)   +0.38  👍 Positive    │  │
│  │  👨‍🔬 Dr. Muthu (Sociology)    +0.25  🙂 Slight Pos  │  │
│  │  👩‍💼 Ms. Wong (IR)            +0.18  🙂 Slight Pos  │  │
│  │  👤 Ahmad (Public)             -0.12  😐 Neutral     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Opinion Evolution Over Rounds:                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Round 0    Round 1    Round 2    Round 3           │  │
│  │   ─●─────────●─────────●─────────●──  Consensus      │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Key Insights:                                              │
│  ✓ Economic fundamentals remain strong                      │
│  ✓ Inflation concerns moderate                              │
│  ✓ Public cost-of-living worries persist                    │
│                                                              │
│  7-Day Forecast:  +0.48 (Improving) 📈                     │
│  30-Day Forecast: +0.55 (Sustained Growth) 📈              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Complete Feature Roadmap

| Phase | Features | Timeline |
|-------|----------|----------|
| **Phase 1** | ✅ Data Collection (170+ items)<br>✅ NLP Analysis<br>✅ Dashboard UI | Complete |
| **Phase 2** | 🔄 MiroFish Integration<br>⏳ Real-Time Alerts<br>⏳ Trend Forecasts | 2-3 weeks |
| **Phase 3** | ⏳ Topic Modeling<br>⏳ Demographic Segmentation<br>⏳ Report Generator | 3-4 weeks |
| **Phase 4** | ⏳ Mobile App<br>⏳ Misinformation Detection<br>⏳ Comparative Analysis | 4-6 weeks |

---

## 🎯 Next Immediate Actions

1. **Test NLP Fix**: Run data collection and verify no more token length errors
2. **Integrate MiroFish**: Follow steps above to add agent discussions
3. **Add Agent Tab**: Create frontend visualization for 6 agents
4. **Deploy & Demo**: Ready for PMX presentation

---

## 💡 Innovative Features for Malaysia Context

### 1. **Bahasa Malaysia Support** 🇲🇾
- Multi-lingual sentiment analysis (BM + English)
- Code-switching detection (Manglish)
- Cultural context understanding

### 2. **Multi-Ethnic Sentiment** 🌏
- Sentiment breakdown by ethnic community
- Cross-cultural issue tracking
- Unity index measurement

### 3. **Policy Impact Tracker** 📋
- Track sentiment before/after policy announcements
- Measure policy effectiveness
- Identify unintended consequences

### 4. **Election Mode** 🗳️
- Constituency-level sentiment
- Manifesto promise tracking
- Political temperature monitoring

---

**Status**: NLP error fixed ✅ | MiroFish integration plan ready ✅ | Feature roadmap defined ✅
