# Citizen Sentiment & Public Opinion Perception System
## Complete Setup Guide for Government Use

---

## 📋 Overview

This system collects **real-time data** from multiple free sources to provide the Prime Minister with:

- **📈 High-Frequency Economic Indicators** - GDP, unemployment, inflation, treasury rates
- **🚨 Crisis & Risk Monitoring** - Disaster declarations, emergency alerts, humanitarian crises
- **🏛️ Service Delivery Metrics** - Government spending, agency performance, wait times
- **💬 Citizen Sentiment** - Reddit discussions, news coverage, public opinion

---

## 🚀 Quick Start (15 minutes)

### Step 1: Install Dependencies

```bash
cd /path/to/govt-project/opinion_sim_system
pip install opinion-sim-system[all]
```

### Step 2: Get API Keys (All FREE)

| API | Purpose | Get Key | Time |
|-----|---------|---------|------|
| **Reddit** | Public sentiment | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) | 2 min |
| **FRED** | Economic data | [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) | 1 min |
| **NewsAPI** | News articles | [newsapi.org/register](https://newsapi.org/register) | 1 min |
| **BLS** | Labor statistics | [bls.gov/developers](https://www.bls.gov/developers/api_registration.htm) | 2 min |

### Step 3: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, code, etc.
```

Add your API keys:
```bash
REDDIT_CLIENT_ID=abc123xyz
REDDIT_CLIENT_SECRET=def456uvw
REDDIT_USER_AGENT=PMOpinionDashboard/1.0 (by /u/your_username)
FRED_API_KEY=your_fred_key
NEWSAPI_KEY=your_newsapi_key
BLS_API_KEY=your_bls_key
```

### Step 4: Collect Data

```bash
# Collect from all sources
python -m opinion_sim_system.data_collection.enhanced_collector

# Or use the CLI tool
python -m opinion_sim_system.data_collection.cli collect --all
```

### Step 5: Generate Dashboard

```bash
# Generate PM dashboard
python -m opinion_sim_system.visualization.pm_dashboard

# Generate briefing report
python -m opinion_sim_system.visualization.briefing_report

# Launch interactive Streamlit app
streamlit run opinion_sim_system/visualization/streamlit_app.py
```

---

## 📊 Data Sources Explained

### 1. High-Frequency Economic Indicators

| Source | Data | Frequency | API Limit |
|--------|------|-----------|-----------|
| **FRED** | GDP, unemployment, inflation, interest rates | Daily | 120/min |
| **BLS** | Employment, CPI, wages | Monthly | 500/hour |
| **BEA** | National accounts, trade | Quarterly | Free |

**Key Indicators Collected:**
- `GDP` - Gross Domestic Product
- `UNRATE` - Unemployment Rate
- `CPIAUCSL` - Consumer Price Index (inflation)
- `PCE` - Personal Consumption Expenditures
- `DGS10` - 10-Year Treasury Rate

### 2. Crisis & Risk Monitoring

| Source | Data | Update | API Limit |
|--------|------|--------|-----------|
| **OpenFEMA** | US disaster declarations | Real-time | Free |
| **GDACS** | Global disaster alerts | Real-time | Free |
| **ReliefWeb** | Humanitarian crises | Hourly | Free |

**Monitors:**
- Natural disasters (hurricanes, earthquakes, floods)
- Emergency declarations
- Humanitarian crises
- Public health emergencies

### 3. Operational & Service Delivery

| Source | Data | Update | API Limit |
|--------|------|--------|-----------|
| **USAspending.gov** | Government spending | Daily | Free |
| **Performance.gov** | Agency metrics | Weekly | Free |
| **Agency APIs** | Wait times, processing | Real-time | Free |

**Metrics:**
- Agency spending by category
- Service wait times (VA, SSA, IRS)
- Processing times for benefits
- Delivery performance (USPS)

### 4. Citizen Sentiment

| Source | Data | Update | API Limit |
|--------|------|--------|-----------|
| **Reddit** | Public discussions | Real-time | 60/min |
| **NewsAPI** | News articles | Real-time | 100/day |
| **GNews** | Global news | Real-time | 100/day |

**Analyzed From:**
- r/news, r/worldnews, r/politics, r/economics
- 70,000+ news sources
- Social media sentiment

---

## 🛠️ Advanced Configuration

### Lightpanda Headless Browser (Optional)

For advanced web scraping (11x faster than Chrome):

```bash
# Install Lightpanda
curl -fsSL https://lightpanda.io/install.sh | sh

# Start Lightpanda server
lightpanda serve

# Configure in .env
LIGHTPANDA_PATH=/usr/local/bin/lightpanda
LIGHTPANDA_WS_URL=ws://localhost:9222
```

### Custom Keywords

Edit in `.env`:
```bash
COLLECTION_KEYWORDS=government policy,healthcare,education,economy,infrastructure
```

### Custom Subreddits

```bash
REDDIT_SUBREDDITS=news,worldnews,politics,economics,your_subreddit
```

### Geographic Focus

```bash
COUNTRY=us
STATE=california
CITY=los_angeles
```

---

## 📁 Output Files

After running collection:

| File | Description | Size |
|------|-------------|------|
| `enhanced_collected_data.json` | Raw collected data | ~10 KB |
| `pm_data_collection.json` | Processed data | ~15 KB |
| `pm_dashboard.html` | Interactive dashboard | ~5 MB |
| `pm_briefing_report.html` | Printable briefing | ~15 KB |
| `real_data_analysis.json` | Sentiment analysis | ~5 KB |

---

## 🎯 CLI Commands

```bash
# Collect all data
pm-data collect --all

# Collect specific categories
pm-data collect --economic
pm-data collect --crisis
pm-data collect --sentiment
pm-data collect --service

# Generate dashboard
pm-data dashboard

# Check status
pm-data status
```

---

## 🔒 Security & Compliance

### Data Handling
- All data collected via official public APIs
- No authentication bypass or rate limit circumvention
- Respects robots.txt and API terms of service
- Data stored locally only

### API Key Security
```bash
# NEVER commit .env to git
# .env is in .gitignore by default

# Rotate keys periodically
# Monitor API usage dashboards
```

### Classification
- Default: `OFFICIAL USE ONLY`
- Modify in `briefing_report.py` if needed
- Add watermarks for distribution

---

## 📈 Free Tier Limits Summary

| API | Free Limit | Suitable For |
|-----|------------|--------------|
| Reddit | 60 req/min | Continuous monitoring |
| FRED | 120 req/min | Real-time economic data |
| BLS | 500 req/hour | Labor statistics |
| NewsAPI | 100 req/day | Daily briefings |
| GNews | 100 req/day | Backup news source |
| OpenFEMA | Unlimited | Disaster monitoring |
| USAspending | Unlimited | Spending tracking |

---

## 🐛 Troubleshooting

### "API key not configured"
```bash
# Check .env file exists
ls -la .env

# Verify keys are set
grep FRED_API_KEY .env
```

### "Rate limit exceeded"
- Wait for limit reset (check API docs)
- Reduce collection frequency
- Use multiple API keys (rotate)

### "No data collected"
- Check internet connection
- Verify API keys are valid
- Try with public datasets fallback

### Lightpanda not working
```bash
# Check installation
lightpanda --version

# Start server
lightpanda serve

# Test connection
curl http://localhost:9222
```

---

## 📞 Support & Resources

### API Documentation
- [FRED API](https://fred.stlouisfed.org/docs/api/fred/)
- [BLS API](https://www.bls.gov/developers/)
- [OpenFEMA](https://www.fema.gov/about/openfema/api)
- [Reddit API](https://www.reddit.com/dev/api/)

### Code Repository
- Location: `/path/to/govt-project/opinion_sim_system`
- Documentation: `README.md`, `data_collection/SETUP.md`

### Example Usage
```python
from data_collection.enhanced_collector import EnhancedDataCollector, CollectorConfig

config = CollectorConfig.from_env()
collector = EnhancedDataCollector(config)
items = collector.collect_all()

print(f"Collected {len(items)} items")
```

---

## ✅ Checklist for Deployment

- [ ] All API keys obtained and configured
- [ ] Dependencies installed (`pip install opinion-sim-system[all]`)
- [ ] `.env` file configured (never commit to git)
- [ ] Test data collection runs successfully
- [ ] Dashboard generates without errors
- [ ] Briefing report prints correctly
- [ ] Security review completed
- [ ] API usage monitoring set up
- [ ] Backup data sources configured
- [ ] Documentation reviewed and approved

---

**Version:** 1.0  
**Last Updated:** 2026-03-29  
**Classification:** OFFICIAL USE ONLY
