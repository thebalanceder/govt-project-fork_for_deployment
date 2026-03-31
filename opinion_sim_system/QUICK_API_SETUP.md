# 🚀 Quick API Setup Guide

## ✅ Step 1: Copy .env.example to .env

```bash
cd /path/to/govt-project/opinion_sim_system
cp .env.example .env
```

---

## ✅ Step 2: Fill in AVAILABLE API Keys

### **REQUIRED** (For Core Functionality)

#### 1. Reddit API - Social Media Data ✅
```bash
# Get from: https://www.reddit.com/prefs/apps
# Time: 5 minutes
# Free tier: 60 requests/minute

REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=CSPOPS/2.0 (by /u/your_username)
```

**How to get:**
1. Go to https://www.reddit.com/prefs/apps
2. Scroll to bottom → "create another app"
3. Select "script"
4. Name: CSPOPS
5. Copy "client_id" (under "personal use script")
6. Copy "client_secret"

---

#### 2. OpenRouter API - AI Analysis ✅
```bash
# Get from: https://openrouter.ai/keys
# Time: 3 minutes
# Free tier: Varies by model

OPENROUTER_API_KEY=your_key_here
USE_OPENROUTER=true
```

**How to get:**
1. Go to https://openrouter.ai/keys
2. Sign up/Login
3. Create API key
4. Copy key

---

### **OPTIONAL** (For More Data)

#### 3. NewsAPI - More News Articles
```bash
# Get from: https://newsapi.org/register
# Time: 2 minutes
# Free tier: 100 requests/day

NEWSAPI_KEY=your_key_here
```

#### 4. GNews - Backup News
```bash
# Get from: https://gnews.io/
# Time: 2 minutes
# Free tier: 100 requests/day

GNEWS_KEY=your_key_here
```

#### 5. FRED - Global Economic Indicators
```bash
# Get from: https://fred.stlouisfed.org/docs/api/api_key.html
# Time: 2 minutes
# Free tier: 120 requests/minute

FRED_API_KEY=your_key_here
```

#### 6. Trading Economics - More Economic Data
```bash
# Get from: https://developer.tradingeconomics.com/
# Time: 3 minutes
# Free tier: 2000 requests/day

TRADING_ECONOMICS_KEY=your_key_here
```

#### 7. Twitter API - Tweets
```bash
# Get from: https://developer.twitter.com/
# Time: 10 minutes (requires approval)
# Free tier: 500 tweets/month

TWITTER_BEARER_TOKEN=your_token_here
```

#### 8. Telegram API - Telegram Channels
```bash
# Get from: https://my.telegram.org/apps
# Time: 5 minutes
# Free tier: Unlimited

TELEGRAM_API_ID=your_id_here
TELEGRAM_API_HASH=your_hash_here
```

---

## ✅ Step 3: Install Required Packages

```bash
# Core packages (REQUIRED)
pip install requests python-dotenv

# Economic data
pip install yfinance

# Social media
pip install praw

# News RSS feeds
pip install feedparser

# Web crawling
pip install playwright
python3 -m playwright install chromium

# Telegram (optional)
pip install telethon
```

---

## ✅ Step 4: Test Collection

```bash
cd /path/to/govt-project
python3 -m opinion_sim_system.data_collection.enhanced_collector
```

**Expected Output:**
```
📊 Collecting Economic Data...
  ✓ Exchange Rate: 31 items
  ✓ KLCI: 60 items
  ✓ Oil Price: 1 items
  ✓ World Bank: 50 items
  ✓ IMF: 30 items
  ...

💬 Collecting Social Media...
  ✓ Reddit: 200 posts
  ✓ Twitter: 100 tweets
  ...

📰 Collecting News...
  ✓ NewsAPI: 30 items
  ✓ RSS Feeds: 40 items
  ...

🏛️ Collecting Government Data...
  ✓ Government: 5 items

TOTAL: 500+ items
```

---

## 📊 Expected Data by API Configuration

### **Minimal Setup** (No API keys):
- Exchange Rate API: 31 items ✅
- Yahoo Finance (KLCI): 60 items ✅
- API Ninjas (Oil): 1 item ✅
- World Bank: 50 items ✅
- IMF: 30 items ✅
- RSS Feeds: 40 items ✅
- Government: 5 items ✅

**Total: ~220 items**

---

### **Standard Setup** (Reddit + NewsAPI):
- All Minimal items: 220 items
- Reddit: 200-400 posts ✅
- NewsAPI: 30 articles ✅
- GNews: 30 articles ✅

**Total: ~500 items**

---

### **Full Setup** (All APIs):
- All Standard items: ~500 items
- FRED: 100-200 indicators ✅
- Trading Economics: 50-100 indicators ✅
- Twitter: 100-400 tweets ✅
- Telegram: 100-200 messages ✅
- Web Crawling: 20 items ✅

**Total: 1,000-1,500+ items**

---

## 🔧 Troubleshooting

### "API key not configured"
→ Add the key to `.env` file

### "Module not found"
→ Install required package: `pip install package_name`

### "Rate limit exceeded"
→ Wait for limit reset (usually 1 hour)

### "API timeout"
→ Check internet connection
→ Reduce `MAX_ITEMS_PER_SOURCE` in `.env`

---

## 📞 API Key Links Summary

| API | Get Key | Time | Free Tier |
|-----|---------|------|-----------|
| **Reddit** | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) | 5 min | 60 req/min |
| **OpenRouter** | [openrouter.ai/keys](https://openrouter.ai/keys) | 3 min | Varies |
| **NewsAPI** | [newsapi.org/register](https://newsapi.org/register) | 2 min | 100 req/day |
| **GNews** | [gnews.io/](https://gnews.io/) | 2 min | 100 req/day |
| **FRED** | [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) | 2 min | 120 req/min |
| **Trading Economics** | [developer.tradingeconomics.com](https://developer.tradingeconomics.com/) | 3 min | 2000 req/day |
| **Twitter** | [developer.twitter.com](https://developer.twitter.com/) | 10 min | 500 tweets/month |
| **Telegram** | [my.telegram.org/apps](https://my.telegram.org/apps) | 5 min | Unlimited |

---

**Start with Reddit + OpenRouter (10 minutes), then add more APIs as needed!** 🇲🇾✨
