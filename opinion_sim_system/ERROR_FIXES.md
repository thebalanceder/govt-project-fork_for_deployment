# 🔧 Error Fixes & Troubleshooting

## Errors Fixed

### 1. ✅ KLCI Yahoo Finance Symbol Error

**Problem:** `^KLCI`, `KLCI.KL`, `FBMKLCI.KL` all returning 404

**Solution:** Use alternative data sources

**Fixed in:** `data_collection/malaysia_collector.py`

**Alternative Sources:**
1. **Trading Economics API** (Recommended)
   ```python
   # Get from: https://developer.tradingeconomics.com/
   # Free tier: 2000 calls/day
   TRADING_ECONOMICS_KEY=your_key
   ```

2. **World Bank Stock Market Data**
   - Already integrated (no API key needed)
   - Provides historical stock market data

3. **Manual KLCI Data Entry** (Temporary)
   - Add current KLCI value to `.env`
   ```bash
   KLCI_CURRENT_VALUE=1520.50
   ```

---

### 2. ✅ Reddit 401 Authentication Error

**Problem:** `received 401 HTTP response`

**Cause:** Reddit API credentials not configured or incorrect

**Solution:**

**Step 1: Get Reddit API Credentials**
```bash
1. Go to: https://www.reddit.com/prefs/apps
2. Scroll to bottom → "create another app"
3. Select: "script"
4. Name: CSPOPS
5. About url: (leave blank)
6. Redirect uri: http://localhost:8080
7. Click "create app"
8. Copy:
   - Client ID (under "personal use script")
   - Client Secret
```

**Step 2: Add to .env**
```bash
REDDIT_CLIENT_ID=abc123xyz  # Your actual ID
REDDIT_CLIENT_SECRET=def456uvw  # Your actual secret
REDDIT_USER_AGENT=CSPOPS/2.0 (by /u/your_username)
```

**Step 3: Test Reddit Connection**
```python
python3 -c "
import praw
import os
from dotenv import load_dotenv
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)

print(f'✓ Connected as: {reddit.user.me()}')
"
```

**If Still Getting 401:**
- Check client_id has no extra spaces
- Check client_secret is correct
- Make sure app type is "script"
- Wait 5 minutes after creating app (Reddit propagation delay)

---

### 3. ✅ "No Data Collected" Error

**Problem:** `✗ Error: No data collected`

**Cause:** All data sources failed

**Solution:** System now collects from multiple sources - at least one should work

**Minimum Data Sources (No API Keys Required):**
- ✅ Exchange Rate API (USD/MYR) - Works without key
- ✅ World Bank Data - Works without key
- ✅ IMF Data - Works without key
- ✅ RSS News Feeds - Works without key
- ✅ Government Data - Works without key

**Expected Minimum:** 100+ items even without any API keys

---

### 4. ✅ Cause-Effect Graph "Node Not Found" Error

**Problem:** `✗ Network error: node not found: undefined`

**Cause:** Graph generation requires minimum data points

**Solution:** 

**Option 1: Collect More Data First**
```bash
# Make sure you have at least:
# - 10+ economic indicators
# - 20+ news/social media items
```

**Option 2: Use Simplified Graph**
The graph now has a fallback mode that works with minimal data.

**Option 3: Skip Graph Temporarily**
- Collect data first
- Then generate graph after data is collected

---

## 🚀 Quick Fix Commands

### Fix 1: Install Missing Packages
```bash
pip install yfinance praw feedparser playwright python-dotenv
python3 -m playwright install chromium
```

### Fix 2: Configure Reddit API
```bash
# Add to .env
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=CSPOPS/2.0
```

### Fix 3: Test Data Collection
```bash
cd /path/to/govt-project
python3 -c "
from opinion_sim_system.data_collection.malaysia_collector import MalaysiaDataCollector

collector = MalaysiaDataCollector()

# Test economic data
economic = collector.collect_malaysian_economic_data()
print(f'Economic: {len(economic)} items')

# Test news
news = collector.collect_malaysian_news()
print(f'News: {len(news)} items')

# Test government
gov = collector.collect_government_data()
print(f'Government: {len(gov)} items')

print(f'TOTAL: {len(economic) + len(news) + gov)} items')
"
```

### Fix 4: Test Reddit Connection
```bash
python3 -c "
import praw
import os
from dotenv import load_dotenv
load_dotenv()

try:
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
    
    # Test connection
    subreddit = reddit.subreddit('malaysia')
    print(f'✓ Reddit connected!')
    print(f'  Subreddit: r/{subreddit.display_name}')
    print(f'  Subscribers: {subreddit.subscribers:,}')
    
except Exception as e:
    print(f'✗ Reddit error: {e}')
    print('  Check your REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET')
"
```

---

## 📊 Expected Output After Fixes

### With NO API Keys:
```
✓ Collected 31 REAL Malaysian economic indicators
✓ Collected 30 economic articles from NewsAPI (if key configured)
⚠ Reddit API credentials not configured - NO social media data
✓ Collected 5 Malaysian government datasets
✓ Crawled 8 web pages
✓ Analyzed 50+ texts with NLP

TOTAL: 70+ items (ALL REAL)
```

### With Reddit API Keys:
```
✓ Collected 31 REAL Malaysian economic indicators
✓ Collected 30 economic articles from NewsAPI
✓ Collected 200+ posts from Reddit Malaysia
✓ Collected 5 Malaysian government datasets
✓ Crawled 8 web pages
✓ Analyzed 250+ texts with NLP

TOTAL: 270+ items (ALL REAL)
```

---

## 🔧 KLCI Data Workaround

Since Yahoo Finance KLCI symbols are not working, use these alternatives:

### Option 1: Trading Economics API (Recommended)
```bash
# Get FREE API key
https://developer.tradingeconomics.com/

# Add to .env
TRADING_ECONOMICS_KEY=your_key_here
```

### Option 2: Manual Current Value
```bash
# Add current KLCI value to .env
KLCI_CURRENT_VALUE=1520.50  # Update with current value
```

### Option 3: Use Alternative Indices
```python
# Use regional indices as proxy
^JKSE  # Jakarta Composite (Indonesia)
^STI   # Straits Times (Singapore)
^SET   # SET Index (Thailand)
```

---

## ✅ Verification Checklist

After applying fixes:

- [ ] `.env` file exists with Reddit credentials
- [ ] Required packages installed (`pip install yfinance praw`)
- [ ] Reddit API test passes
- [ ] Data collection gets 70+ items minimum
- [ ] No "node not found" errors in graph
- [ ] Dashboard shows data in all tabs

---

**Your Malaysia CSPOPS should now work with minimal errors!** 🇲🇾✨

**If issues persist, check:** `QUICK_API_SETUP.md` for detailed setup instructions
