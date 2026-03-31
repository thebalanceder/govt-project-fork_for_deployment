"""
Integration Patch: Add crawled news loading to MalaysiaDataCollector

Add these TWO functions to malaysia_collector.py
"""

def _load_crawled_news(self) -> List[DataItem]:
    """Load previously crawled Malaysian news from data/malaysian_news/"""
    items = []
    
    try:
        # Path to crawled news directory
        news_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'malaysian_news'
        
        if not news_dir.exists():
            return items
        
        categories = ['economic', 'political', 'cultural']
        
        for category in categories:
            cat_dir = news_dir / category
            if not cat_dir.exists():
                continue
            
            # Load summary files
            summary_files = list(cat_dir.glob('summary_*.json'))
            
            for summary_file in summary_files:
                try:
                    data = json.loads(summary_file.read_text(encoding='utf-8'))
                    articles = data.get('articles', [])
                    
                    for article in articles:
                        content = article.get('content', '')
                        if not content or len(content) < 100:
                            continue
                        
                        items.append(DataItem(
                            id=f"crawled_{category}_{article.get('title', '')[:30]}",
                            source="Malaysian News Crawler",
                            category="news",
                            text=content[:500],
                            timestamp=datetime.now(),
                            url=article.get('url', ''),
                            title=article.get('title', ''),
                            metadata={
                                'category': category,
                                'date': article.get('date', ''),
                                'author': article.get('author', ''),
                                'crawled': True,
                                'real_time': True
                            }
                        ))
                except Exception:
                    pass
        
        if items:
            print(f"  ✓ Loaded {len(items)} crawled news articles")
    
    except Exception as e:
        print(f"  Error loading crawled news: {e}")
    
    return items


def collect_malaysian_news_with_crawler(self) -> List[DataItem]:
    """
    Collect news from BOTH crawler AND APIs.
    """
    items = []
    
    if not REQUESTS_AVAILABLE:
        return items
    
    # FIRST: Load crawled Malaysian news
    crawled_items = self._load_crawled_news()
    if crawled_items:
        items.extend(crawled_items)
    
    newsapi_key = os.getenv('NEWSAPI_KEY', '')
    gnews_key = os.getenv('GNEWS_KEY', '')
    
    # SECOND: NewsAPI
    if newsapi_key:
        try:
            response = requests.get(
                'https://newsapi.org/v2/everything',
                params={
                    'q': 'Malaysia economy OR Bank Negara OR KLCI OR ringgit OR inflation',
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'apiKey': newsapi_key,
                    'pageSize': 30
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                start_count = len(items)
                for article in data.get('articles', []):
                    items.append(DataItem(
                        id=f"newsapi_{article.get('title', '')[:50]}",
                        source=article.get('source', {}).get('name', 'Unknown'),
                        category="news",
                        text=f"{article.get('title', '')}\n\n{article.get('description', '')}",
                        timestamp=datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')) if article.get('publishedAt') else datetime.now(),
                        url=article.get('url', ''),
                        title=article.get('title', ''),
                        metadata={
                            'country': 'Malaysia',
                            'source_type': 'news_api',
                            'real_time': True
                        }
                    ))
                if len(items) > start_count:
                    print(f"✓ Collected {len(items) - start_count} articles from NewsAPI")
        except Exception as e:
            print(f"NewsAPI error: {e}")
    
    # THIRD: GNews API
    if gnews_key:
        try:
            response = requests.get(
                'https://gnews.io/api/v4/search',
                params={
                    'q': 'Malaysia economy inflation Bank Negara',
                    'lang': 'en',
                    'country': 'my',
                    'max': 30,
                    'apikey': gnews_key
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                start_count = len(items)
                for article in data.get('articles', []):
                    items.append(DataItem(
                        id=f"gnews_{article.get('title', '')[:50]}",
                        source=article.get('source', {}).get('name', 'Unknown'),
                        category="news",
                        text=f"{article.get('title', '')}\n\n{article.get('description', '')}",
                        timestamp=datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')) if article.get('publishedAt') else datetime.now(),
                        url=article.get('url', ''),
                        title=article.get('title', ''),
                        metadata={
                            'country': 'Malaysia',
                            'source_type': 'gnews',
                            'real_time': True
                        }
                    ))
                if len(items) > start_count:
                    print(f"✓ Collected {len(items) - start_count} articles from GNews")
        except Exception as e:
            print(f"GNews error: {e}")
    
    # FOURTH: RSS feeds
    try:
        import feedparser
        
        rss_feeds = [
            'https://www.thestar.com.my/rss/business',
            'https://www.nst.com.my/rss/business',
            'https://www.theedgemarkets.com/rss',
        ]
        
        start_count = len(items)
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    items.append(DataItem(
                        id=f"rss_{entry.link[:50]}",
                        source=feed.feed.get('title', 'RSS Feed'),
                        category="news",
                        text=f"{entry.title}",
                        timestamp=datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                        url=entry.link,
                        title=entry.title,
                        metadata={
                            'country': 'Malaysia',
                            'source_type': 'rss',
                            'real_time': True
                        }
                    ))
            except Exception:
                pass
        
        if len(items) > start_count:
            print(f"✓ Collected {len(items) - start_count} articles from RSS feeds")
    except ImportError:
        print("⚠ feedparser not installed")
    
    print(f"✓ Total collected {len(items)} news articles (crawled + APIs)")
    return items
