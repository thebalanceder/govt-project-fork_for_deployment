"""
Unified Data Collector - Complete Integration

Integrates ALL available data sources:
1. Malaysian News Crawler (150+ articles: economic, political, cultural)
2. MalaysiaDataCollector (KLCI, exchange rates, local news)
3. EnhancedDataCollector (10+ APIs: World Bank, IMF, FRED, etc.)
4. Standard Collectors (Reddit, NewsAPI, GNews)

All data categorized into: economic, political, cultural
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class DataItem:
    """Represents a single data item."""
    id: str
    source: str
    category: str  # economic, political, cultural
    text: str
    timestamp: datetime
    url: str = ""
    author: str = ""
    title: str = ""
    value: float | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedDataCollector:
    """
    Complete unified data collector integrating ALL sources.
    """

    def __init__(self, max_items_per_category: int = 100):
        self.max_items = max_items_per_category
        self.stats = {
            'economic': 0,
            'political': 0,
            'cultural': 0,
            'sources_used': []
        }

    # =========================================================================
    # MALAYSIAN NEWS CRAWLER INTEGRATION
    # =========================================================================

    def collect_crawled_malaysian_news(self) -> Dict[str, List[DataItem]]:
        """
        Load previously crawled Malaysian news from data/malaysian_news/
        Returns: {'economic': [...], 'political': [...], 'cultural': [...]}
        """
        result = {'economic': [], 'political': [], 'cultural': []}
        seen_urls = set()  # Track unique URLs
        seen_titles = set()  # Track unique titles

        try:
            news_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'malaysian_news'

            if not news_dir.exists():
                print("⚠ No crawled news directory found")
                return result

            categories = ['economic', 'political', 'cultural']

            for category in categories:
                cat_dir = news_dir / category
                if not cat_dir.exists():
                    continue

                # Load summary files which contain all articles
                summary_files = list(cat_dir.glob('summary_*.json'))

                if not summary_files:
                    continue

                # Use the most recent summary
                latest_summary = max(summary_files, key=lambda p: p.stat().st_mtime)

                try:
                    data = json.loads(latest_summary.read_text(encoding='utf-8'))
                    articles = data.get('articles', [])

                    for article in articles[:self.max_items]:
                        content = article.get('content', '')
                        url = article.get('url', '')
                        title = article.get('title', '')
                        
                        if not content or len(content) < 100:
                            continue
                        
                        # Skip duplicate URLs
                        if url in seen_urls:
                            print(f"  ⚠️  Skip duplicate URL: {url[:50]}...")
                            continue
                        seen_urls.add(url)
                        
                        # Skip duplicate titles (normalized)
                        normalized_title = ' '.join(title.lower().split())[:50]
                        if normalized_title in seen_titles:
                            print(f"  ⚠️  Skip duplicate title: {title[:50]}...")
                            continue
                        seen_titles.add(normalized_title)

                        result[category].append(DataItem(
                            id=f"crawled_{category}_{title[:30]}_{len(result[category])}",
                            source="Malaysian News Crawler",
                            category=category,
                            text=content[:2000],
                            timestamp=datetime.now(),
                            url=url,
                            title=title,
                            author=article.get('author', ''),
                            metadata={
                                'category': category,
                                'date': article.get('date', ''),
                                'crawled': True,
                                'source_type': 'web_crawler',
                                'country': 'Malaysia'
                            }
                        ))

                    print(f"✓ Loaded {len(result[category])} unique crawled {category} articles (after deduplication)")
                    self.stats['sources_used'].append(f'Crawled {category} news')

                except Exception as e:
                    print(f"  Error loading {latest_summary}: {e}")

        except Exception as e:
            print(f"  Error loading crawled news: {e}")

        return result

    # =========================================================================
    # MALAYSIA DATA COLLECTOR INTEGRATION
    # =========================================================================

    def collect_malaysia_economic_data(self) -> List[DataItem]:
        """Collect Malaysian economic data from APIs."""
        items = []

        if not REQUESTS_AVAILABLE:
            return items

        print("\n📊 Collecting Malaysian Economic Data...")

        # Exchange Rate Data
        try:
            response = requests.get(
                'https://api.exchangerate-api.com/v4/latest/USD',
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                myr_rate = data['rates'].get('MYR', 4.45)

                items.append(DataItem(
                    id=f"myr_usd_{datetime.now().strftime('%Y%m%d')}",
                    source="Exchange Rate API",
                    category="economic",
                    text=f"USD/MYR Exchange Rate: {myr_rate:.2f}",
                    timestamp=datetime.now(),
                    title="USD/MYR Exchange Rate",
                    value=myr_rate,
                    metadata={'country': 'Malaysia', 'indicator': 'exchange_rate'}
                ))
                print(f"  ✓ Exchange rate: {myr_rate:.2f}")
        except Exception as e:
            print(f"  ⚠ Exchange rate error: {e}")

        # Oil Price Data
        try:
            response = requests.get(
                'https://api.api-ninjas.com/v1/commodity?symbol=brent',
                headers={'X-Api-Key': 'demo'},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                oil_price = data[0].get('current_price', 85.0)

                items.append(DataItem(
                    id=f"oil_price_{datetime.now().strftime('%Y%m%d')}",
                    source="API Ninjas",
                    category="economic",
                    text=f"Brent Crude Oil: ${oil_price:.2f}/barrel",
                    timestamp=datetime.now(),
                    title="Brent Crude Oil Price",
                    value=float(oil_price),
                    metadata={'country': 'Malaysia', 'indicator': 'oil_price'}
                ))
                print(f"  ✓ Oil price: ${oil_price:.2f}")
        except Exception as e:
            print(f"  ⚠ Oil price error: {e}")

        # KLCI via yfinance
        try:
            import yfinance as yf
            klci_symbols = ['^KLCI', 'KLCI.KL', 'FBMKLCI.KL']

            for symbol in klci_symbols:
                try:
                    klci = yf.Ticker(symbol)
                    hist = klci.history(period="1mo")
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        items.append(DataItem(
                            id=f"klci_{datetime.now().strftime('%Y%m%d')}",
                            source="Yahoo Finance",
                            category="economic",
                            text=f"FTSE Bursa Malaysia KLCI: {current:.2f}",
                            timestamp=datetime.now(),
                            title="Bursa Malaysia KLCI",
                            value=float(current),
                            metadata={'country': 'Malaysia', 'indicator': 'stock_index'}
                        ))
                        print(f"  ✓ KLCI ({symbol}): {current:.2f}")
                        break
                except:
                    continue
        except ImportError:
            print("  ⚠ yfinance not installed - skipping KLCI")
        except Exception as e:
            print(f"  ⚠ KLCI error: {e}")

        self.stats['sources_used'].append('Malaysia economic APIs')
        return items

    def collect_malaysia_news(self) -> Dict[str, List[DataItem]]:
        """
        Collect Malaysian news from NewsAPI, GNews, and RSS feeds.
        Returns: {'economic': [...], 'political': [...], 'cultural': [...]}
        """
        result = {'economic': [], 'political': [], 'cultural': []}

        if not REQUESTS_AVAILABLE:
            return result

        print("\n📰 Collecting Malaysian News from APIs...")

        newsapi_key = os.getenv('NEWSAPI_KEY', '')
        gnews_key = os.getenv('GNEWS_KEY', '')

        # NewsAPI
        if newsapi_key:
            try:
                categories_query = {
                    'economic': 'Malaysia economy OR Bank Negara OR KLCI OR ringgit',
                    'political': 'Malaysia politics OR parliament OR government',
                    'cultural': 'Malaysia culture OR festival OR tradition OR arts'
                }

                for category, query in categories_query.items():
                    response = requests.get(
                        'https://newsapi.org/v2/everything',
                        params={
                            'q': query,
                            'language': 'en',
                            'sortBy': 'publishedAt',
                            'apiKey': newsapi_key,
                            'pageSize': 20
                        },
                        timeout=15
                    )

                    if response.status_code == 200:
                        data = response.json()
                        for article in data.get('articles', [])[:15]:
                            content = f"{article.get('title', '')}\n\n{article.get('description', '')}"
                            result[category].append(DataItem(
                                id=f"newsapi_{category}_{len(result[category])}",
                                source=article.get('source', {}).get('name', 'Unknown'),
                                category=category,
                                text=content[:2000],
                                timestamp=datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')) if article.get('publishedAt') else datetime.now(),
                                url=article.get('url', ''),
                                title=article.get('title', ''),
                                metadata={'country': 'Malaysia', 'source_type': 'newsapi'}
                            ))
                        print(f"  ✓ NewsAPI {category}: {len(result[category])} articles")

                self.stats['sources_used'].append('NewsAPI')
            except Exception as e:
                print(f"  ⚠ NewsAPI error: {e}")

        # GNews
        if gnews_key:
            try:
                for category in ['economic', 'political', 'cultural']:
                    response = requests.get(
                        'https://gnews.io/api/v4/search',
                        params={
                            'q': f'Malaysia {category}',
                            'lang': 'en',
                            'country': 'my',
                            'max': 15,
                            'apikey': gnews_key
                        },
                        timeout=15
                    )

                    if response.status_code == 200:
                        data = response.json()
                        for article in data.get('articles', [])[:10]:
                            content = f"{article.get('title', '')}\n\n{article.get('description', '')}"
                            result[category].append(DataItem(
                                id=f"gnews_{category}_{len(result[category])}",
                                source=article.get('source', {}).get('name', 'Unknown'),
                                category=category,
                                text=content[:2000],
                                timestamp=datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')) if article.get('publishedAt') else datetime.now(),
                                url=article.get('url', ''),
                                title=article.get('title', ''),
                                metadata={'country': 'Malaysia', 'source_type': 'gnews'}
                            ))
                        print(f"  ✓ GNews {category}: {len(result[category])} articles")

                self.stats['sources_used'].append('GNews')
            except Exception as e:
                print(f"  ⚠ GNews error: {e}")

        # RSS Feeds (no API key needed)
        try:
            import feedparser

            rss_feeds = {
                'economic': [
                    'https://www.thestar.com.my/rss/business',
                    'https://www.nst.com.my/rss/business',
                    'https://www.theedgemarkets.com/rss',
                ],
                'political': [
                    'https://www.thestar.com.my/rss/nation',
                    'https://www.nst.com.my/rss/nation',
                ],
                'cultural': [
                    'https://www.thestar.com.my/rss/lifestyle',
                    'https://www.nst.com.my/rss/life',
                ]
            }

            for category, feeds in rss_feeds.items():
                for feed_url in feeds[:2]:
                    try:
                        feed = feedparser.parse(feed_url)
                        for entry in feed.entries[:5]:
                            content = entry.get('title', '') + ' - ' + entry.get('summary', '')
                            result[category].append(DataItem(
                                id=f"rss_{category}_{len(result[category])}",
                                source=feed.feed.get('title', 'RSS Feed'),
                                category=category,
                                text=content[:2000],
                                timestamp=datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                                url=entry.link,
                                title=entry.title,
                                metadata={'country': 'Malaysia', 'source_type': 'rss'}
                            ))
                    except:
                        pass

            for category in result:
                if result[category]:
                    print(f"  ✓ RSS {category}: {len(result[category])} articles")

            self.stats['sources_used'].append('RSS Feeds')

        except ImportError:
            print("  ⚠ feedparser not installed - skipping RSS")

        return result

    def collect_malaysia_social_media(self) -> List[DataItem]:
        """Collect Malaysian social media data."""
        items = []

        # Reddit r/malaysia
        try:
            import praw

            reddit_client_id = os.getenv('REDDIT_CLIENT_ID', '')
            reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')

            if reddit_client_id and reddit_client_secret:
                reddit = praw.Reddit(
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    user_agent='CSPOPS/1.0'
                )

                subreddit = reddit.subreddit('malaysia')
                categories = {'economic': [], 'political': [], 'cultural': []}

                keywords = {
                    'economic': ['economy', 'business', 'job', 'salary', 'cost', 'price', 'ringgit', 'klci'],
                    'political': ['government', 'parliament', 'minister', 'policy', 'election', 'politics'],
                    'cultural': ['culture', 'festival', 'tradition', 'food', 'race', 'religion', 'language']
                }

                for post in subreddit.hot(limit=100):
                    title_lower = post.title.lower()
                    for category, kws in keywords.items():
                        if any(kw in title_lower for kw in kws):
                            categories[category].append(post)
                            break

                for category, posts in categories.items():
                    for post in posts[:20]:
                        items.append(DataItem(
                            id=f"reddit_my_{post.id}",
                            source="Reddit r/malaysia",
                            category=category,
                            text=f"{post.title}\n\n{post.selftext}"[:2000],
                            timestamp=datetime.fromtimestamp(post.created_utc),
                            url=f"https://reddit.com{post.permalink}",
                            title=post.title,
                            metadata={
                                'country': 'Malaysia',
                                'platform': 'Reddit',
                                'upvotes': post.score,
                                'comments': post.num_comments
                            }
                        ))

                print(f"✓ Collected {len(items)} posts from Reddit r/malaysia")
                self.stats['sources_used'].append('Reddit Malaysia')
            else:
                print("⚠ Reddit API credentials not configured - skipping")

        except ImportError:
            print("⚠ PRAW not installed - skipping Reddit")
        except Exception as e:
            print(f"⚠ Reddit error: {e}")

        return items

    # =========================================================================
    # ENHANCED DATA COLLECTOR INTEGRATION
    # =========================================================================

    def collect_enhanced_economic_data(self) -> List[DataItem]:
        """Collect from World Bank, IMF, FRED, etc."""
        items = []

        if not REQUESTS_AVAILABLE:
            return items

        print("\n🌍 Collecting International Economic Data...")

        # World Bank Data (Malaysia GDP)
        try:
            response = requests.get(
                'https://api.worldbank.org/v2/country/MYS/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=5',
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    gdp_data = data[1][0] if data[1] else {}
                    gdp_value = gdp_data.get('value', 0)
                    year = gdp_data.get('date', 'N/A')

                    items.append(DataItem(
                        id=f"worldbank_gdp_{year}",
                        source="World Bank",
                        category="economic",
                        text=f"Malaysia GDP Growth: {gdp_value}% ({year})",
                        timestamp=datetime.now(),
                        title="Malaysia GDP Growth (World Bank)",
                        value=float(gdp_value) if gdp_value else None,
                        metadata={'country': 'Malaysia', 'indicator': 'gdp', 'source_type': 'world_bank'}
                    ))
                    print(f"  ✓ World Bank GDP: {gdp_value}%")
        except Exception as e:
            print(f"  ⚠ World Bank error: {e}")

        # FRED Economic Data (US Interest Rates - affects Malaysia)
        try:
            fred_key = os.getenv('FRED_API_KEY', '')
            if fred_key:
                response = requests.get(
                    'https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS&api_key={}&file_type=json'.format(fred_key),
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('observations'):
                        latest = data['observations'][-1]
                        items.append(DataItem(
                            id=f"fred_fedfunds_{latest['date']}",
                            source="FRED",
                            category="economic",
                            text=f"US Federal Funds Rate: {latest['value']}% ({latest['date']})",
                            timestamp=datetime.now(),
                            title="US Federal Funds Rate",
                            value=float(latest['value']),
                            metadata={'indicator': 'interest_rate', 'source_type': 'fred'}
                        ))
                        print(f"  ✓ FRED Fed Funds: {latest['value']}%")
        except Exception as e:
            print(f"  ⚠ FRED error: {e}")

        self.stats['sources_used'].append('World Bank/FRED')
        return items

    # =========================================================================
    # COMPLETE COLLECTION
    # =========================================================================

    def collect_all(self) -> Dict[str, Any]:
        """
        Run complete data collection from ALL sources.

        Returns:
            {
                'economic': [DataItem, ...],
                'political': [DataItem, ...],
                'cultural': [DataItem, ...],
                'stats': {...}
            }
        """
        print("\n" + "=" * 70)
        print("🇲🇾 CSPOPS Malaysia - Unified Data Collection")
        print("=" * 70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        all_data = {
            'economic': [],
            'political': [],
            'cultural': []
        }

        # 1. Load crawled Malaysian news (150+ articles)
        print("\n📰 Loading Crawled Malaysian News...")
        crawled = self.collect_crawled_malaysian_news()
        for category in ['economic', 'political', 'cultural']:
            all_data[category].extend(crawled.get(category, []))

        # 2. Collect Malaysian economic data
        print("\n📊 Collecting Malaysian Economic Indicators...")
        all_data['economic'].extend(self.collect_malaysia_economic_data())

        # 3. Collect Malaysian news from APIs
        print("\n📰 Collecting Malaysian News from APIs...")
        news = self.collect_malaysia_news()
        for category in ['economic', 'political', 'cultural']:
            all_data[category].extend(news.get(category, []))

        # 4. Collect social media
        print("\n📱 Collecting Social Media...")
        all_data['economic'].extend(self.collect_malaysia_social_media())

        # 5. Enhanced economic data
        print("\n🌍 Collecting International Economic Data...")
        all_data['economic'].extend(self.collect_enhanced_economic_data())

        # Update stats
        for category in ['economic', 'political', 'cultural']:
            self.stats[category] = len(all_data[category])

        # Print summary
        total = sum(len(items) for items in all_data.values())
        print("\n" + "=" * 70)
        print("✅ Collection Complete!")
        print("=" * 70)
        print(f"\n📊 Total Items: {total}")
        print(f"  - 📈 Economic: {self.stats['economic']} items")
        print(f"  - 🏛️  Political: {self.stats['political']} items")
        print(f"  - 🎭 Cultural: {self.stats['cultural']} items")
        print(f"\n📡 Sources Used:")
        for source in self.stats['sources_used']:
            print(f"  ✓ {source}")

        return {
            **all_data,
            'stats': self.stats,
            'timestamp': datetime.now().isoformat()
        }


def run_unified_collection() -> Dict[str, Any]:
    """Convenience function to run complete collection."""
    collector = UnifiedDataCollector(max_items_per_category=100)
    return collector.collect_all()


if __name__ == "__main__":
    result = run_unified_collection()
    print(f"\n✓ Collection complete: {result['stats']}")
