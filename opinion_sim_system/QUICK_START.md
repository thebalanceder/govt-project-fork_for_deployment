# 🚀 CSPOPS Quick Start Guide

## ✅ System Ready!

Your beautiful Flask-based CSPOPS dashboard is now running!

---

## 🌐 Access Dashboard

### **Open your browser:**
```
http://localhost:5000
```

---

## 📋 Step-by-Step Usage

### 1. Collect Real-Time Data
1. Click **"Data Collection"** tab
2. Click **"Collect Real-Time Data"** button
3. Wait 30-60 seconds for collection
4. You'll see: "✓ Data collection complete!"

### 2. View Dashboard
After collection completes:
- **Dashboard tab** automatically shows
- **🔴 LIVE badge** appears with timestamp
- **4 Sentiment Cards** display:
  - Overall Sentiment (emoji + score)
  - Positive %
  - Negative %
  - Neutral %
- **Emotion Breakdown** section with:
  - Bar chart
  - Dominant emotion highlight
  - AI insight

### 3. Generate Cause-Effect Graph
1. Click **"Cause-Effect Graph"** tab
2. Click **"Generate AI Cause-Effect Map"** button
3. Wait 30-60 seconds for AI analysis
4. **Interactive graph appears!**

### 5. Explore Graph
- **Drag nodes** to reposition
- **Scroll** to zoom in/out
- **Click & drag** empty space to pan
- **Hover** nodes/edges for details
- **Expand** "View All Nodes/Relationships" for lists
- **Download** graph as JSON

### 6. Chat with AI
1. Click **"AI Chat"** tab
2. Type question: "What's the current sentiment?"
3. Get instant AI response
4. Ask follow-up questions

### 7. Generate Summary
1. Go to **Dashboard** tab
2. Click **"Generate Executive Summary"**
3. AI writes 3-paragraph report
4. Read or copy summary

---

## 🎯 Graph Interaction Guide

### Node Interactions
- **Click & Drag** - Reposition node
- **Hover** - See full details (name, group, value)
- **Color** indicates group:
  - 🔵 Blue = Economic
  - 🟢 Green = Sentiment
  - 🟣 Purple = Emotion
  - 🔴 Red = Crisis
  - 🟠 Orange = Service

### Edge Interactions
- **Hover** - See relationship description:
  - Relationship type (causes, influences, etc.)
  - Strength (0.5-1.0)
  - Strength description (Weak/Moderate/Strong/Very Strong)
- **Arrow direction** - Shows influence direction

### Viewport Controls
- **Mouse Wheel** - Zoom in/out
- **Click & Drag** empty space - Pan around
- **Double-click** - Reset zoom

---

## 📊 What Each Tab Shows

### Dashboard
- Sentiment cards (4 metrics)
- Emotion breakdown (chart + highlight)
- Quick action buttons
- Executive summary (after generation)

### Economy
- Economic indicators list
- Values and dates
- Trend information

### Sentiment
- NLP analysis results
- Article sources breakdown
- Word frequency

### Crises
- Active disaster declarations
- Emergency alerts
- Crisis count

### Services
- Government agency metrics
- Performance data
- Spending information

### Cause-Effect Graph ⭐
- AI-generated network graph
- 10-15 nodes
- 15-20 relationships
- AI insights
- Interactive visualization
- Downloadable data

### AI Chat
- Chat interface
- Ask anything about the data
- Get AI-powered answers

### Data Collection
- One-click collection button
- Progress bar
- Results summary

---

## 🔧 Troubleshooting

### "No module named 'opinion_sim_system'"
**Fix:** The Flask app already has the path fixed. Just refresh the page.

### "API key not configured"
**Fix:** Add your API key to `.env` file:
```bash
# Edit .env in opinion_sim_system/
OPENROUTER_API_KEY=sk-or-v1-your-key-here
USE_OPENROUTER=true
```

### Graph not appearing
**Fix:** 
1. Make sure data is collected first
2. Click "Generate AI Cause-Effect Map"
3. Wait full 60 seconds
4. Check browser console for errors (F12)

### Chat not responding
**Fix:** 
1. Ensure API key is configured
2. Collect data first (chat needs context)
3. Check network tab (F12 → Network)

---

## 📁 Project Structure

```
govt-project/
├── opinion_sim_system/
│   ├── flask_app.py              ← Flask backend (RUN THIS)
│   ├── flask_app/
│   │   ├── templates/
│   │   │   └── index.html        ← Main HTML
│   │   └── static/
│   │       ├── css/
│   │       │   └── style.css     ← Styling
│   │       └── js/
│   │           ├── app.js        ← App logic
│   │           └── graph.js      ← D3.js graph
│   ├── ai/
│   │   ├── chatbot.py            ← AI chatbot
│   │   └── cause_effect.py       ← Graph generator
│   ├── nlp/
│   │   └── advanced_analyzer.py  ← NLP analysis
│   ├── data_collection/
│   │   ├── collector.py          ← Data collectors
│   │   └── enhanced_collector.py ← Enhanced collectors
│   └── .env                      ← API keys
```

---

## 🎯 Quick Commands

### Start Application
```bash
cd /path/to/govt-project
python3 -m opinion_sim_system.flask_app
```

### Check if Running
```bash
ps aux | grep flask
```

### Stop Application
```bash
pkill -f flask
```

### View Logs
```bash
tail -f /tmp/flask.log
```

---

## 🎨 Features Checklist

- [x] Beautiful professional UI
- [x] D3.js force-directed graph
- [x] Detailed edge descriptions
- [x] Drag/zoom/pan interactions
- [x] Color-coded nodes
- [x] Graph legend
- [x] Node/edge lists
- [x] JSON download
- [x] AI insights
- [x] Sentiment cards
- [x] Emotion chart
- [x] Live badge
- [x] AI chatbot
- [x] Executive summary
- [x] Data collection
- [x] Responsive design
- [x] RESTful API
- [x] Real-time updates

---

## 📞 Support

**Documentation:**
- `FLASK_APP_GUIDE.md` - Complete Flask guide
- `SIMPLE_EXPLANATIONS.md` - Feature explanations
- `UI_ENHANCEMENTS.md` - UI improvement ideas
- `NLP_FEATURES.md` - NLP features guide

**API Setup:**
- `AI_SETUP.md` - API key setup

---

## 🎉 You're Ready!

**Your CSPOPS dashboard is live and ready for the PMX visit!**

**Access:** http://localhost:5000

**Enjoy your beautiful, professional dashboard!** 🏛️✨
