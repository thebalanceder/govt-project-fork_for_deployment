# 🏛️ CSPOPS - Beautiful Flask Web Application

## ✅ Complete Rewrite - No More Streamlit!

I've completely rewritten the application using **Flask + D3.js** for a professional, beautiful, and fully customizable web experience.

---

## 🌐 Access Your New Dashboard

### **http://localhost:5000**

---

## 🎨 What's New & Beautiful

### 1. **Professional Government-Grade UI**
- Gradient header with live badge
- Sticky navigation bar
- Clean, modern card designs
- Responsive layout
- Professional color scheme

### 2. **Interactive D3.js Cause-Effect Graph**
- **Force-directed graph** - Nodes repel each other naturally
- **Drag nodes** - Reposition by dragging
- **Zoom & Pan** - Mouse wheel to zoom, drag to pan
- **Detailed tooltips** - Hover to see full information
- **Color-coded nodes** - By group (economic, sentiment, emotion, etc.)
- **Labeled edges** - Shows relationship type and strength
- **Arrow indicators** - Shows direction of influence

### 3. **Enhanced Edge Descriptions**

Each edge now shows:
```
From Node → To Node
Relationship: 🔵 Strongly influences
Strength: 0.8/1.0 (Very Strong)
```

**Relationship Types:**
| Type | Icon | Description |
|------|------|-------------|
| `causes` | 🔴 | Directly causes |
| `influences` | 🔵 | Strongly influences |
| `triggers` | ⚡ | Triggers or activates |
| `correlates_with` | 📊 | Statistically correlates with |
| `leads_to` | ➡️ | Leads to over time |
| `affects` | 💫 | Affects or impacts |
| `drives` | 🚀 | Drives or pushes |

### 4. **Graph Features**

**Interactive Controls:**
- Click and drag nodes to reposition
- Mouse wheel to zoom in/out
- Click and drag empty space to pan
- Hover over nodes for details
- Hover over edges for relationship info

**Graph Legend:**
- Color-coded by group
- Clear instructions
- Node/edge counts

**Expandable Details:**
- View all nodes with values
- View all relationships with descriptions
- Download graph as JSON

---

## 📊 Dashboard Sections

### Executive Dashboard
1. **🔴 LIVE Badge** - Shows last update time
2. **4 Sentiment Cards**:
   - Overall Sentiment (emoji + score + classification)
   - Positive percentage
   - Negative percentage
   - Neutral percentage
3. **Emotion Breakdown**:
   - Interactive Plotly bar chart
   - Dominant emotion highlight card
   - AI-generated insight
4. **Quick Actions**:
   - Generate AI Cause-Effect Map
   - Generate Executive Summary

### Economy Tab
- Economic indicators list
- Trend charts
- Historical data

### Sentiment Tab
- NLP analysis results
- Article list by source
- Word frequency

### Crises Tab
- Active disaster declarations
- Emergency alerts
- Crisis timeline

### Services Tab
- Government performance metrics
- Agency spending data
- Service delivery stats

### 🕸️ Cause-Effect Graph Tab (NEW!)
- **AI Generate Button** - Creates graph from all data
- **Loading Animation** - Shows AI analysis progress
- **Graph Insights** - AI-discovered relationships
- **Interactive Graph** - D3.js force-directed visualization
- **Legend** - Color codes and instructions
- **Node/Edge Lists** - Expandable details
- **Download Button** - Export as JSON

### AI Chat Tab
- Chat interface
- Ask questions about data
- Get AI-powered answers

### Data Collection Tab
- One-click data collection
- Progress bar
- Results summary

---

## 🎯 How to Use

### 1. Start the Application
```bash
cd /path/to/govt-project
python3 -m opinion_sim_system.flask_app
```

### 2. Open Browser
```
http://localhost:5000
```

### 3. Collect Data
- Click "Data Collection" tab
- Click "Collect Real-Time Data"
- Wait for completion

### 4. View Dashboard
- Automatically shows sentiment cards
- Emotion chart renders
- Summary available

### 5. Generate Cause-Effect Graph
- Click "Cause-Effect Graph" tab
- Click "Generate AI Cause-Effect Map"
- Wait 30-60 seconds for AI analysis
- **Explore the interactive graph!**

### 6. Interact with Graph
- **Drag nodes** to reposition
- **Scroll** to zoom in/out
- **Hover** nodes/edges for details
- **Expand** node/edge lists
- **Download** as JSON

---

## 🎨 Visual Features

### Sentiment Cards
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   😊         │     😊       │     😞       │     😐       │
│  +0.65       │    65%       │    15%       │    20%       │
│  POSITIVE    │  Positive    │  Negative    │   Neutral    │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

### Emotion Highlight
```
┌─────────────────────────┐
│         😊              │
│   Dominant Emotion      │
│        Joy              │
│         35%             │
│                         │
│ ✅ Positive public mood │
│ - good time for policy  │
│   announcements         │
└─────────────────────────┘
```

### Cause-Effect Graph
```
[D3.js Force-Directed Graph]

    🔵 DGS10 ──────→ 🟢 Sentiment
     (4.42%)  influences  (+0.65)
       │          ↑
       │          │
       ↓          │
    🟣 Joy ←──────┘
    (35%)   triggers
```

---

## 📁 File Structure

```
opinion_sim_system/
├── flask_app.py                    # Flask backend
├── flask_app/
│   ├── templates/
│   │   └── index.html             # Main HTML template
│   └── static/
│       ├── css/
│       │   └── style.css          # Beautiful styling
│       └── js/
│           ├── app.js             # Main application logic
│           └── graph.js           # D3.js graph visualization
├── ai/
│   ├── chatbot.py                 # AI chatbot
│   └── cause_effect.py            # AI graph generator
└── nlp/
    └── advanced_analyzer.py       # NLP analysis
```

---

## 🔧 Technical Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask (Python) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Graph Visualization** | D3.js v7 |
| **Charts** | Plotly.js |
| **Icons** | Font Awesome 6 |
| **HTTP** | RESTful API |
| **AI** | OpenRouter/DeepSeek API |

---

## 🎯 Key Improvements Over Streamlit

| Feature | Streamlit | Flask + D3.js |
|---------|-----------|---------------|
| **Customization** | Limited | Unlimited |
| **Graph Beauty** | Basic | Professional |
| **Edge Descriptions** | Simple | Detailed with icons |
| **Interactivity** | Limited | Full drag/zoom/pan |
| **UI Design** | Template-based | Fully custom |
| **Performance** | Good | Excellent |
| **Scalability** | Limited | Production-ready |
| **Branding** | Streamlit logo | Your branding |

---

## 🚀 Features Summary

### ✅ Implemented
- [x] Beautiful professional UI
- [x] D3.js force-directed graph
- [x] Detailed edge descriptions
- [x] Drag/zoom/pan interactions
- [x] Color-coded nodes
- [x] Graph legend
- [x] Node/edge lists
- [x] JSON download
- [x] AI insights display
- [x] Sentiment cards
- [x] Emotion chart
- [x] Live badge
- [x] AI chatbot
- [x] Executive summary
- [x] Data collection
- [x] Responsive design

---

## 📖 Usage Examples

### Generate Graph
1. Collect data
2. Go to "Cause-Effect Graph" tab
3. Click "Generate AI Cause-Effect Map"
4. Wait for AI analysis
5. Explore interactive graph

### Interpret Graph
- **Nodes** = Concepts (economic indicators, emotions, etc.)
- **Edges** = Relationships (causes, influences, etc.)
- **Colors** = Groups (blue=economic, green=sentiment, etc.)
- **Arrow direction** = Direction of influence
- **Edge thickness** = Relationship strength
- **Hover** = See detailed descriptions

### Chat with AI
1. Go to "AI Chat" tab
2. Type question: "What's the sentiment?"
3. Get instant AI response
4. Ask follow-up questions

---

## 🎉 Your System Is Now Production-Ready!

**Beautiful UI** ✅  
**Interactive Graphs** ✅  
**Detailed Edge Descriptions** ✅  
**Professional Design** ✅  
**No Streamlit** ✅  

---

**Access:** http://localhost:5000

**Enjoy your beautiful new dashboard!** 🏛️✨
