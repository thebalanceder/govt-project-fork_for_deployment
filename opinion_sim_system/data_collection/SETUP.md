# Real Data Collection Setup Guide

## Quick Start - Get API Keys (5 minutes)

### Step 1: Reddit API (Required for Reddit data)

1. Go to https://www.reddit.com/prefs/apps
2. Scroll to "developed applications" → Click "create another app"
3. Fill in:
   - **name**: PMOpinionDashboard
   - **Select**: "script"
   - **redirect uri**: http://localhost:8080
4. Click "create app"
5. Copy your credentials:
   - **Client ID**: The string under "personal use script" (e.g., `abc123xyz`)
   - **Client Secret**: The "secret" field (e.g., `def456uvw`)

### Step 2: NewsAPI (Required for news articles)

1. Go to https://newsapi.org/register
2. Enter your email
3. Click "Send API Key"
4. Copy your API key from the email

### Step 3: GNews API (Optional - backup news source)

1. Go to https://gnews.io/
2. Click "Get API Key"
3. Register with email
4. Copy your API key

### Step 4: Configure Environment

1. Copy the example file:
   ```bash
   cd opinion_sim_system
   cp .env.example .env
   ```

2. Edit `.env` and add your keys:
   ```
   REDDIT_CLIENT_ID=abc123xyz
   REDDIT_CLIENT_SECRET=def456uvw
   NEWSAPI_KEY=your_newsapi_key
   GNEWS_KEY=your_gnews_key
   ```

### Step 5: Install Dependencies

```bash
# Install data collection dependencies
pip install opinion-sim-system[data]

# Or install everything
pip install opinion-sim-system[all]
```

### Step 6: Run Data Collection

```bash
# Collect real data and generate dashboard
python -m opinion_sim_system.data_collection.run_pipeline
```

---

## API Free Tier Limits

| API | Free Tier | Suitable For |
|-----|-----------|--------------|
| **Reddit (PRAW)** | 60 requests/min | Continuous monitoring |
| **NewsAPI** | 100 requests/day | Daily briefings |
| **GNews** | 100 requests/day | Backup news source |
| **Public Datasets** | Unlimited | Fallback data |

---

## Troubleshooting

### "No API keys configured"
- Make sure `.env` file exists in `opinion_sim_system/` directory
- Check that keys are correctly copied (no extra spaces)

### "Rate limit exceeded"
- NewsAPI/GNews: Wait 24 hours or use multiple API keys
- Reddit: Wait 1 minute between requests

### "No data collected"
- Check internet connection
- Verify API keys are valid
- Try different keywords
- Public datasets will be used as fallback

---

## Data Sources Explained

### Reddit
- **What**: Public discussions from news/politics subreddits
- **Pros**: Real-time public sentiment, unfiltered opinions
- **Cons**: Skews younger demographic

### NewsAPI
- **What**: News articles from 70,000+ sources
- **Pros**: Professional journalism, broad coverage
- **Cons**: 100 requests/day limit

### GNews
- **What**: Global news aggregation
- **Pros**: International perspective
- **Cons**: 100 requests/day limit

### Public Datasets
- **What**: Pre-collected sentiment data
- **Pros**: No API keys needed, instant
- **Cons**: Not real-time

---

## Customization

### Change Keywords

Edit in `run_pipeline.py`:
```python
default_keywords = [
    "your topic 1",
    "your topic 2",
]
```

### Change Subreddits

In `.env`:
```
REDDIT_SUBREDDITS=news,worldnews,politics,your_subreddit
```

### Increase Data Collection

In `.env`:
```
MAX_ITEMS_PER_SOURCE=200
DAYS_BACK=14
```

---

## Output Files

After running the pipeline:

| File | Description |
|------|-------------|
| `collected_data.json` | Raw collected data (cached) |
| `real_data_analysis.json` | Analyzed data with sentiment |
| `pm_dashboard_real.html` | Interactive dashboard |
| `pm_briefing_real.html` | Printable briefing report |

---

## Security Notes

- `.env` file is gitignored - never commit API keys
- API keys are stored locally only
- No data is sent to external servers (except API requests)
- Suitable for government use with proper security review

---

## Support

For issues:
1. Check API key validity
2. Review error messages
3. Try with public datasets only (no API keys needed)
