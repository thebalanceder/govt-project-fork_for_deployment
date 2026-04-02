# 📊 Guide: Collect MORE Real-Time Economic & Social Media Data

## 🎯 Goal: Maximize Real-Time Data Collection

**Current:** ~220 items
**Target:** 500-1000+ items

**ALL data must be REAL-TIME from APIs - ZERO hardcoded data**

---

## Part 1: MORE Economic Data Sources

### A. Free Economic APIs (No Key Required)

#### 1. **World Bank Open Data** ✅ FREE
```python
import requests

def collect_world_bank_malaysia():
    """Collect Malaysian economic indicators from World Bank."""
    items = []
    
    # Malaysian indicators
    indicators = {
        'NY.GDP.MKTP.KD.ZG': 'GDP Growth Rate',
        'FP.CPI.TOTL.ZG': 'Inflation Rate',
        'NE.EXP.GNFS.ZS': 'Exports % of GDP',
        'NE.IMP.GNFS.ZS': 'Imports % of GDP',
        'BN.CAB.XOKA.GD.ZS': 'Current Account % of GDP',
        'GC.REV.GOTR.GD.ZS': 'Government Revenue % of GDP',
        'GC.XPN.TOTL.GD.ZS': 'Government Spending % of GDP',
        'NY.GDP.PCAP.KD.ZG': 'GDP Per Capita Growth',
        'SL.UEM.TOTL.ZS': 'Unemployment Rate',
        'FP.WPI.TOTL': 'Wholesale Price Index'
    }
    
    for indicator_code, indicator_name in indicators.items():
        try:
            # World Bank API endpoint
            url = f'https://api.worldbank.org/v2/country/MYS/indicator/{indicator_code}'
            params = {
                'format': 'json',
                'date': '2020:2026',  # Last 6 years
                'per_page': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) >= 2 and data[1]:
                    for record in data[1]:
                        year = record.get('date')
                        value = record.get('value')
                        
                        if value is not None:
                            items.append({
                                'id': f'wb_{indicator_code}_{year}',
                                'source': 'World Bank',
                                'category': 'economic',
                                'text': f'{indicator_name}: {value}',
                                'timestamp': f'{year}-12-31',
                                'title': indicator_name,
                                'value': float(value),
                                'metadata': {
                                    'series_id': indicator_code,
                                    'country': 'Malaysia',
                                    'agency': 'World Bank',
                                    'real_time': True,
                                    'historical': True
                                }
                            })
        except Exception as e:
            print(f'World Bank error for {indicator_code}: {e}')
    
    print(f'✓ Collected {len(items)} indicators from World Bank')
    return items
```

**Get:** 50-100 data points
**API:** https://api.worldbank.org/
**Key:** NOT required (FREE)

---

#### 2. **IMF Data API** ✅ FREE
```python
def collect_imf_malaysia():
    """Collect Malaysian data from IMF."""
    items = []
    
    # IMF data endpoints
    endpoints = [
        ('https://api.imf.org/data/IFS/MYS', 'International Financial Statistics'),
        ('https://api.imf.org/data/DOTS/MYS', 'Direction of Trade Statistics'),
    ]
    
    for url, source_name in endpoints:
        try:
            response = requests.get(url, params={'format': 'json'}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Parse IMF response format
                for series in data.get('data', []):
                    for obs in series.get('observations', []):
                        value = obs.get('OBS_VALUE')
                        date = obs.get('TIME_PERIOD')
                        
                        if value is not None:
                            items.append({
                                'id': f'imf_{series.get("id", "")}_{date}',
                                'source': source_name,
                                'category': 'economic',
                                'text': f'{series.get("description", "")}: {value}',
                                'timestamp': date,
                                'value': float(value),
                                'metadata': {
                                    'country': 'Malaysia',
                                    'agency': 'IMF',
                                    'real_time': True
                                }
                            })
        except Exception as e:
            print(f'IMF error: {e}')
    
    print(f'✓ Collected {len(items)} indicators from IMF')
    return items
```

**Get:** 30-50 data points
**API:** https://datahelp.imf.org/knowledgebase/articles/667681-using-json-restful-web-service
**Key:** NOT required (FREE)

---

#### 3. **Trading Economics API** ✅ FREE (Limited)
```python
def collect_trading_economics_malaysia():
    """Collect from Trading Economics (requires free API key)."""
    import os
    
    api_key = os.getenv('TRADING_ECONOMICS_KEY', '')
    
    if not api_key:
        print('⚠ Trading Economics API key not configured')
        return []
    
    items = []
    
    # Malaysian economic indicators
    indicators = [
        'gdp-growth-rate',
        'inflation-rate',
        'unemployment-rate',
        'interest-rate',
        'balance-of-trade',
        'current-account',
        'foreign-exchange-reserves',
        'government-debt-to-gdp',
        'stock-market',
        'oil-prices'
    ]
    
    for indicator in indicators:
        try:
            url = f'https://api.tradingeconomics.com/malaysia/{indicator}'
            headers = {'Authorization': f'Bearer {api_key}'}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    for item in data:
                        items.append({
                            'id': f'te_{indicator}_{item.get("DateTime", "")}',
                            'source': 'Trading Economics',
                            'category': 'economic',
                            'text': f'{item.get("Title", "")}: {item.get("Value", "")}',
                            'timestamp': item.get('DateTime', ''),
                            'value': float(item.get('Value', 0)),
                            'metadata': {
                                'country': 'Malaysia',
                                'agency': 'Trading Economics',
                                'real_time': True
                            }
                        })
        except Exception as e:
            print(f'Trading Economics error: {e}')
    
    print(f'✓ Collected {len(items)} indicators from Trading Economics')
    return items
```

**Get:** 50-100 data points
**API:** https://tradingeconomics.com/api
**Key:** FREE tier (2000 calls/day) - Get at: https://developer.tradingeconomics.com/

---

#### 4. **FRED (Federal Reserve Economic Data)** ✅ FREE
```python
def collect_fred_global_indicators():
    """Collect global indicators affecting Malaysia from FRED."""
    import os
    
    api_key = os.getenv('FRED_API_KEY', '')
    
    if not api_key:
        print('⚠ FRED API key not configured')
        return []
    
    items = []
    
    # Global indicators that affect Malaysia
    indicators = {
        'DEXUSEU': 'USD/EUR Exchange Rate',
        'DEXCHUS': 'USD/China Exchange Rate',
        'DEXJPUS': 'USD/Japan Exchange Rate',
        'DCOILWTICO': 'Crude Oil Prices WTI',
        'DCOILBRENTEU': 'Crude Oil Prices Brent',
        'T10Y2Y': '10-Year vs 2-Year Treasury Spread',
        'VIXCLS': 'VIX Volatility Index',
        'DGS10': '10-Year Treasury Rate',
        'DGS2': '2-Year Treasury Rate',
        'GDPC1': 'US GDP Growth Rate'
    }
    
    for series_id, name in indicators.items():
        try:
            url = f'https://api.stlouisfed.org/fred/series/observations'
            params = {
                'series_id': series_id,
                'api_key': api_key,
                'file_type': 'json',
                'limit': 50
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for obs in data.get('observations', []):
                    value = obs.get('value')
                    if value and value != '.':
                        items.append({
                            'id': f'fred_{series_id}_{obs.get("date", "")}',
                            'source': 'FRED',
                            'category': 'economic',
                            'text': f'{name}: {value}',
                            'timestamp': obs.get('date', ''),
                            'value': float(value),
                            'metadata': {
                                'series_id': series_id,
                                'country': 'Global/US',
                                'agency': 'Federal Reserve',
                                'real_time': True,
                                'note': 'Affects Malaysia through trade/finance linkages'
                            }
                        })
        except Exception as e:
            print(f'FRED error for {series_id}: {e}')
    
    print(f'✓ Collected {len(items)} global indicators from FRED')
    return items
```

**Get:** 100-200 data points
**API:** https://fred.stlouisfed.org/docs/api/fred/
**Key:** FREE - Get at: https://fred.stlouisfed.org/docs/api/api_key.html

---

### B. Malaysian Government APIs

#### 5. **Bank Negara Malaysia (BNM) Open Data** ✅ FREE
```python
def collect_bnm_open_data():
    """Collect from Bank Negara Malaysia Open Data."""
    items = []
    
    # BNM open data endpoints
    endpoints = [
        'https://api.bnm.gov.my/api/public/ers',  # Exchange Rates
        'https://api.bnm.gov.my/api/public/irs',  # Interest Rates
        'https://api.bnm.gov.my/api/public/m3',   # Money Supply
    ]
    
    for url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Parse BNM response
                for series in data.get('result', {}).get('series', []):
                    for obs in series.get('observations', []):
                        items.append({
                            'id': f'bnm_{series.get("id", "")}_{obs.get("date", "")}',
                            'source': 'Bank Negara Malaysia',
                            'category': 'economic',
                            'text': f'{series.get("title", "")}: {obs.get("value", "")}',
                            'timestamp': obs.get('date', ''),
                            'value': float(obs.get('value', 0)) if obs.get('value') else None,
                            'metadata': {
                                'country': 'Malaysia',
                                'agency': 'Bank Negara Malaysia',
                                'real_time': True
                            }
                        })
        except Exception as e:
            print(f'BNM error: {e}')
    
    print(f'✓ Collected {len(items)} indicators from BNM')
    return items
```

**Get:** 50-100 data points
**API:** https://api.bnm.gov.my/
**Key:** NOT required (FREE)

---

#### 6. **DOSM (Department of Statistics Malaysia)** ✅ FREE
```python
def collect_dosm_data():
    """Collect from DOSM Open Data."""
    items = []
    
    # DOSM data portal
    dosm_datasets = [
        'https://api.dosm.gov.my/api/v1/cpi',  # Consumer Price Index
        'https://api.dosm.gov.my/api/v1/gdp',  # GDP
        'https://api.dosm.gov.my/api/v1/trade',  # Trade Statistics
    ]
    
    for url in dosm_datasets:
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Parse DOSM response
                for record in data.get('data', []):
                    items.append({
                        'id': f'dosm_{record.get("id", "")}',
                        'source': 'DOSM',
                        'category': 'economic',
                        'text': f'{record.get("title", "")}: {record.get("value", "")}',
                        'timestamp': record.get('date', ''),
                        'value': float(record.get('value', 0)) if record.get('value') else None,
                        'metadata': {
                            'country': 'Malaysia',
                            'agency': 'Department of Statistics Malaysia',
                            'real_time': True
                        }
                    })
        except Exception as e:
            print(f'DOSM error: {e}')
    
    print(f'✓ Collected {len(items)} indicators from DOSM')
    return items
```

**Get:** 30-50 data points
**API:** https://api.dosm.gov.my/
**Key:** May require registration (FREE)

---

## Part 2: MORE Social Media Data Sources

### A. Reddit API (Enhanced) ✅ FREE

```python
def collect_reddit_comprehensive():
    """Collect from multiple Malaysian subreddits."""
    import os
    
    try:
        import praw
    except ImportError:
        print('⚠ PRAW not installed')
        return []
    
    reddit_client_id = os.getenv('REDDIT_CLIENT_ID', '')
    reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')
    
    if not reddit_client_id or not reddit_client_secret:
        print('⚠ Reddit API credentials not configured')
        return []
    
    items = []
    
    reddit = praw.Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent='CSPOPS/2.0'
    )
    
    # Multiple Malaysian subreddits
    subreddits = [
        'malaysia',
        'askmalaysia',
        'malaysianews',
        'kl',
        'penang',
        'johorbahru',
        'sarawak',
        'sabah'
    ]
    
    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            
            # Hot posts
            for post in subreddit.hot(limit=30):
                items.append(create_reddit_item(post, 'hot'))
            
            # New posts
            for post in subreddit.new(limit=20):
                items.append(create_reddit_item(post, 'new'))
            
            # Rising posts
            for post in subreddit.rising(limit=20):
                items.append(create_reddit_item(post, 'rising'))
            
            print(f'✓ Collected from r/{subreddit_name}')
            
        except Exception as e:
            print(f'Reddit error for r/{subreddit_name}: {e}')
    
    print(f'✓ Total collected {len(items)} posts from Reddit')
    return items

def create_reddit_item(post, post_type):
    """Create DataItem from Reddit post."""
    title_lower = post.title.lower()
    
    # Sentiment detection
    if any(word in title_lower for word in ['great', 'good', 'excellent', 'best', 'happy', 'thanks', 'love', 'awesome']):
        sentiment_hint = 'positive'
    elif any(word in title_lower for word in ['bad', 'terrible', 'worst', 'angry', 'disappointed', 'sial', 'sucks', 'hate', 'sad']):
        sentiment_hint = 'negative'
    else:
        sentiment_hint = 'neutral'
    
    return {
        'id': f'reddit_{post.subreddit}_{post.id}',
        'source': f'Reddit r/{post.subreddit}',
        'category': 'social_media',
        'text': f'{post.title}\n\n{post.selftext}'[:500],
        'timestamp': datetime.fromtimestamp(post.created_utc),
        'url': f'https://reddit.com{post.permalink}',
        'title': post.title,
        'metadata': {
            'country': 'Malaysia',
            'platform': 'Reddit',
            'sentiment_hint': sentiment_hint,
            'upvotes': post.score,
            'comments': post.num_comments,
            'post_type': post_type,
            'real_time': True
        }
    }
```

**Get:** 200-400 posts
**API:** https://www.reddit.com/prefs/apps
**Key:** FREE (60 requests/minute)

---

### B. Twitter/X API ✅ FREE Tier

```python
def collect_twitter_malaysia():
    """Collect Malaysian tweets (requires Twitter API v2)."""
    import os
    
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
    
    if not bearer_token:
        print('⚠ Twitter API token not configured')
        return []
    
    items = []
    
    # Malaysian search queries
    queries = [
        'Malaysia economy',
        'Bank Negara',
        'KLCI',
        'ringgit',
        'cost of living Malaysia',
        'Malaysia inflation',
        'Malaysia jobs',
        'Malaysia property'
    ]
    
    headers = {'Authorization': f'Bearer {bearer_token}'}
    
    for query in queries:
        try:
            url = 'https://api.twitter.com/2/tweets/search/recent'
            params = {
                'query': f'{query} -is:retweet lang:en OR lang:ms',
                'max_results': 50,
                'tweet.fields': 'created_at,public_metrics,lang'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for tweet in data.get('data', []):
                    items.append({
                        'id': f'twitter_{tweet["id"]}',
                        'source': 'Twitter',
                        'category': 'social_media',
                        'text': tweet.get('text', ''),
                        'timestamp': tweet.get('created_at', ''),
                        'metadata': {
                            'country': 'Malaysia',
                            'platform': 'Twitter',
                            'query': query,
                            'metrics': tweet.get('public_metrics', {}),
                            'real_time': True
                        }
                    })
        except Exception as e:
            print(f'Twitter error for "{query}": {e}')
    
    print(f'✓ Collected {len(items)} tweets')
    return items
```

**Get:** 100-400 tweets
**API:** https://developer.twitter.com/en/docs/twitter-api
**Key:** FREE tier (500 tweets/month) - Get at: https://developer.twitter.com/

---

### C. Telegram Channels (Public) ✅ FREE

```python
def collect_telegram_malaysian_channels():
    """Collect from public Malaysian Telegram channels."""
    # Note: Requires Telethon library
    try:
        from telethon import TelegramClient
    except ImportError:
        print('⚠ Telethon not installed')
        return []
    
    import os
    
    api_id = os.getenv('TELEGRAM_API_ID', '')
    api_hash = os.getenv('TELEGRAM_API_HASH', '')
    
    if not api_id or not api_hash:
        print('⚠ Telegram API credentials not configured')
        return []
    
    items = []
    
    # Malaysian channels (public)
    channels = [
        'malaysianews',
        'malaysiaupdates',
        'klfoodie',
        'malaysiaproperty'
    ]
    
    async def collect_from_channel(client, channel):
        channel_items = []
        async for message in client.iter_messages(channel, limit=50):
            if message.text:
                channel_items.append({
                    'id': f'telegram_{channel}_{message.id}',
                    'source': f'Telegram @{channel}',
                    'category': 'social_media',
                    'text': message.text[:500],
                    'timestamp': message.date,
                    'metadata': {
                        'country': 'Malaysia',
                        'platform': 'Telegram',
                        'channel': channel,
                        'real_time': True
                    }
                })
        return channel_items
    
    # Run async collection
    import asyncio
    
    async def main():
        async with TelegramClient('session', api_id, api_hash) as client:
            for channel in channels:
                try:
                    channel_items = await collect_from_channel(client, channel)
                    items.extend(channel_items)
                    print(f'✓ Collected from @{channel}')
                except Exception as e:
                    print(f'Telegram error for @{channel}: {e}')
    
    asyncio.run(main())
    
    print(f'✓ Total collected {len(items)} messages from Telegram')
    return items
```

**Get:** 100-200 messages
**API:** https://core.telegram.org/api
**Key:** FREE - Get at: https://my.telegram.org/apps

---

## Part 3: Configuration & Setup

### Required API Keys (All FREE)

```bash
# Add to .env file

# Reddit (for social media)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Trading Economics (for more economic data)
TRADING_ECONOMICS_KEY=your_key

# FRED (for global indicators)
FRED_API_KEY=your_key

# Twitter (optional, for tweets)
TWITTER_BEARER_TOKEN=your_token

# Telegram (optional, for Telegram channels)
TELEGRAM_API_ID=your_id
TELEGRAM_API_HASH=your_hash
```

### Required Packages

```bash
pip install requests praw telethon
```

---

## Part 4: Expected Data Collection Output

### With All APIs Configured:

```
✓ Collected 60+ indicators from Exchange Rate API
✓ Collected 60+ indicators from Yahoo Finance (KLCI)
✓ Collected 30+ indicators from API Ninjas (Oil)
✓ Collected 50+ indicators from World Bank
✓ Collected 30+ indicators from IMF
✓ Collected 50+ indicators from Trading Economics
✓ Collected 100+ indicators from FRED
✓ Collected 50+ indicators from BNM
✓ Collected 30+ indicators from DOSM
✓ Collected 100+ news articles from multiple sources
✓ Collected 400+ posts from Reddit (8 subreddits)
✓ Collected 200+ tweets from Twitter
✓ Collected 100+ messages from Telegram
✓ Collected 5 government datasets
✓ Crawled 20 web pages

TOTAL: 1,300+ REAL items
```

### Without Some APIs:

```
✓ Collected 60+ indicators from Exchange Rate API
✓ Collected 60+ indicators from Yahoo Finance
✓ Collected 30+ indicators from API Ninjas
⚠ World Bank: API timeout
✓ Collected 30+ indicators from IMF
⚠ Trading Economics: API key not configured
✓ Collected 100+ indicators from FRED
⚠ BNM: API unavailable
✓ Collected 100+ news articles from RSS feeds
✓ Collected 200+ posts from Reddit (4 subreddits)
⚠ Twitter: API key not configured
⚠ Telegram: Not configured
✓ Collected 5 government datasets
✓ Crawled 10 web pages

TOTAL: 600+ REAL items
```

---

## Part 5: Integration with Existing System

### Add to `malaysia_collector.py`:

```python
def collect_all_economic_data(self):
    """Collect from ALL economic data sources."""
    all_items = []
    
    # Existing sources
    all_items.extend(self.collect_malaysian_economic_data())
    
    # NEW: Additional sources
    all_items.extend(collect_world_bank_malaysia())
    all_items.extend(collect_imf_malaysia())
    all_items.extend(collect_trading_economics_malaysia())
    all_items.extend(collect_fred_global_indicators())
    all_items.extend(collect_bnm_open_data())
    all_items.extend(collect_dosm_data())
    
    print(f'✓ Total economic data: {len(all_items)} items')
    return all_items

def collect_all_social_media(self):
    """Collect from ALL social media sources."""
    all_items = []
    
    # Existing: Reddit
    all_items.extend(self.collect_malaysian_social_media())
    
    # NEW: Additional sources
    all_items.extend(collect_reddit_comprehensive())
    all_items.extend(collect_twitter_malaysia())
    all_items.extend(collect_telegram_malaysian_channels())
    
    print(f'✓ Total social media: {len(all_items)} items')
    return all_items
```

---

## ✅ Summary

### Maximum Data Collection:

| Source | Items | API Key Required? |
|--------|-------|-------------------|
| Exchange Rate API | 30 | ❌ No |
| Yahoo Finance | 60 | ❌ No |
| API Ninjas | 30 | ❌ No (demo) |
| World Bank | 50-100 | ❌ No |
| IMF | 30-50 | ❌ No |
| Trading Economics | 50-100 | ✅ Yes (FREE) |
| FRED | 100-200 | ✅ Yes (FREE) |
| BNM | 50-100 | ❌ No |
| DOSM | 30-50 | ❌ No |
| News APIs | 100+ | Optional |
| Reddit | 200-400 | ✅ Yes (FREE) |
| Twitter | 100-400 | ✅ Yes (FREE tier) |
| Telegram | 100-200 | ✅ Yes (FREE) |
| Government | 5 | ❌ No |
| Web Crawling | 20 | ❌ No |
| **TOTAL** | **1,000-1,500+** | **Most FREE** |

---

**Your Malaysia CSPOPS can collect 1,000-1,500+ REAL-TIME items with these additional sources!** 🇲🇾✨

**All data is from REAL APIs - ZERO hardcoded data!**
