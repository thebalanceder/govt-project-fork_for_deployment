# PM Executive Dashboard - Web Application Guide

## 🚀 Quick Start

### 1. Start the Web Application

```bash
cd /path/to/govt-project

# Start the web server
streamlit run opinion_sim_system/web_app/app.py
```

### 2. Open in Browser

The application will automatically open in your default browser at:
**http://localhost:8501**

Or manually navigate to: `http://localhost:8501`

---

## 📊 Features

### Dashboard Tab
- **Executive Overview** - Key metrics at a glance
- **10-Year Treasury Rate** - Real-time from FRED
- **Unemployment Rate** - Latest monthly data
- **News Articles** - Count from last 24 hours
- **Active Crises** - Real-time monitoring

### Economy Tab
- **Real-Time Economic Indicators** from FRED:
  - DGS10: 10-Year Treasury Rate (daily)
  - DGS2: 2-Year Treasury Rate (daily)
  - UNRATE: Unemployment Rate (monthly)
  - CPIAUCSL: Consumer Price Index (monthly)
  - VIXCLS: Volatility Index (daily)
- **BLS Labor Statistics** (monthly)

### Sentiment Tab
- **News Articles** from NewsAPI & GNews (last 24 hours)
- **Reddit Discussions** (real-time)
- **Source Breakdown** - See where sentiment is coming from
- **Recent Mentions** - Expandable articles

### Crises Tab
- **FEMA Disaster Declarations** (US)
- **ReliefWeb Humanitarian Crises** (global)
- **Real-time alerts** with severity indicators

### Services Tab
- **Government Spending** by agency
- **Performance Metrics** (wait times, processing times)
- **Agency Performance** scores

### Data Collection Tab
- **One-Click Collection** from all sources
- **Selective Collection** - Choose which sources to collect from
- **Progress Indicator** - Watch collection status
- **Collection Summary** - See what was collected

### Settings Tab
- **API Status** - See which APIs are configured
- **Get API Keys** - Direct links to register
- **Data Management** - Clear collected data

---

## 🎯 How to Use

### Collect Real-Time Data

1. **Sidebar Button** (Quickest):
   - Click "🔄 Collect Real-Time Data" in the sidebar
   - Wait for collection to complete
   - Dashboard updates automatically

2. **Data Collection Tab** (More Control):
   - Go to "📥 Data Collection" tab
   - Select which sources to collect from
   - Click "🚀 Start Data Collection"
   - Watch progress bar
   - View collection summary

### View Economic Indicators

1. Go to "📈 Economy" tab
2. See all indicators with status badges:
   - 🟢 Low/Good
   - 🟡 Normal
   - 🔴 High/Concerning
3. Hover over values for details

### Monitor Sentiment

1. Go to "💬 Sentiment" tab
2. See breakdown by source
3. Expand recent mentions to read full articles
4. Click links to view original sources

### Track Crises

1. Go to "🚨 Crises" tab
2. See active disaster declarations
3. View crisis details and links
4. Monitor humanitarian situations

---

## ⚙️ Configuration

### API Keys

Go to "⚙️ Settings" tab to see API status and get keys:

| API | Purpose | Get Key |
|-----|---------|---------|
| FRED | Economic data | [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) |
| NewsAPI | News articles | [newsapi.org](https://newsapi.org/register) |
| Reddit | Social sentiment | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) |
| BLS | Labor statistics | [bls.gov/developers](https://www.bls.gov/developers/api_registration.htm) |

### Environment File

Create/edit `.env` in the `opinion_sim_system` directory:

```bash
# API Keys
FRED_API_KEY=your_fred_key
NEWSAPI_KEY=your_newsapi_key
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
BLS_API_KEY=your_bls_key
```

---

## 📁 Data Storage

Collected data is saved to:
```
opinion_sim_system/artifacts/phase1/web_app_data.json
```

This file is automatically loaded when you restart the app.

---

## 🔄 Auto-Refresh

The dashboard does NOT auto-refresh by default. To get fresh data:

1. Click "🔄 Collect Real-Time Data" in sidebar
2. Or go to Data Collection tab and collect again

**Recommended refresh frequency:**
- Economic data: Every 15 minutes (market hours)
- News/Sentiment: Every hour
- Crisis data: Every 30 minutes
- Full collection: Every 6 hours

---

## 🎨 Customization

### Change Theme

Edit `web_app/app.py` and modify the CSS in `setup_page()`:

```python
# Change gradient colors
background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);

# Change accent color
border-left: 4px solid #667eea;
```

### Add Custom Metrics

In `render_metric_cards()`:

```python
st.metric(
    label="Your Metric",
    value="123",
    delta="Updated"
)
```

---

## 🐛 Troubleshooting

### App won't start
```bash
# Check Streamlit is installed
pip install streamlit

# Try different port
streamlit run opinion_sim_system/web_app/app.py --server.port 8502
```

### No data showing
- Click "Collect Real-Time Data" button
- Check API keys are configured
- Check internet connection

### Collection fails
- Check error message in UI
- Verify API keys are valid
- Check rate limits (NewsAPI: 100/day)

### Browser doesn't open automatically
- Manually go to: http://localhost:8501
- Or check terminal for the correct URL

---

## 📊 Sample Dashboard Views

### Executive Summary View
- Dashboard tab: Overall metrics
- Economy tab: Key indicators
- Crises tab: Active alerts

### Analyst View
- Data Collection tab: Full data pull
- Sentiment tab: Detailed analysis
- Settings tab: API management

### Monitoring View
- Dashboard tab: Quick status
- Crises tab: Real-time alerts
- Sidebar: Quick refresh button

---

## 🔒 Security

- All data stored locally
- API keys in `.env` (gitignored)
- No external data sharing
- Suitable for government use

---

## 📞 Support

For issues or feature requests, check:
- Documentation: `COMPLETE_SETUP.md`
- Data Collection Guide: `data_collection/SETUP.md`
- Main README: `README.md`

---

**Version:** 1.0  
**Last Updated:** 2026-03-29  
**Classification:** OFFICIAL USE ONLY
