#!/usr/bin/env python3
"""
Malaysian News Crawler: Economic, Political, and Cultural News
爬取马来西亚新闻：经济、政治、文化
Crawls Bernama, The Star, NST, Malaysiakini for 50 news per category
"""

import re
import time
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# 请求头，模拟浏览器
HEADERS = {
    "User-Agent": "CSPOPS-Crawler/1.0 (Malaysian news collection; educational)",
    "Accept": "text/html,application/xhtml+xml,application/json",
    "Accept-Language": "en,zh,ms;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# 请求间隔（秒），避免对目标站造成压力
DELAY = 2.0
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "malaysian_news"
REQUEST_TIMEOUT = 30

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ========== 经济新闻 (Economic News) ==========
ECONOMIC_NEWS_URLS = [
    # The Star Business (More reliable)
    ("https://www.thestar.com.my/business", "The Star Business", "经济"),
    ("https://www.thestar.com.my/business/economy", "The Star Economy", "经济"),
    ("https://www.thestar.com.my/business/markets", "The Star Markets", "经济"),
    # NST Business
    ("https://www.nst.com.my/business", "NST Business", "经济"),
    ("https://www.nst.com.my/business/economy", "NST Economy", "经济"),
    # The Edge
    ("https://www.theedgemarkets.com/", "The Edge Markets", "经济"),
    # Free Malaysia Today
    ("https://www.freemalaysiatoday.com/category/business/", "FMT Business", "经济"),
    # Malaysiakini
    ("https://www.malaysiakini.com/news/economy", "Malaysiakini Economy", "经济"),
    # Malay Mail Business
    ("https://www.malaymail.com/news/money", "Malay Mail Business", "经济"),
    # Borneo Post Business
    ("https://www.theborneopost.com/category/business-economy/", "Borneo Post Business", "经济"),
    # CodeBlue (healthcare economics)
    ("https://codeblue.galencentre.org/", "CodeBlue Health Economics", "经济"),
    # Focus Malaysia
    ("https://focusmalaysia.my/category/business/", "Focus Malaysia Business", "经济"),
]

# ========== 政治新闻 (Political News) ==========
POLITICAL_NEWS_URLS = [
    # The Star Politics
    ("https://www.thestar.com.my/news/nation", "The Star Nation", "政治"),
    ("https://www.thestar.com.my/news/politics", "The Star Politics", "政治"),
    # NST Politics
    ("https://www.nst.com.my/news/nation", "NST Nation", "政治"),
    ("https://www.nst.com.my/news/politics", "NST Politics", "政治"),
    # Malaysiakini Politics
    ("https://www.malaysiakini.com/news/politics", "Malaysiakini Politics", "政治"),
    # Free Malaysia Today
    ("https://www.freemalaysiatoday.com/category/nation/", "FMT Nation", "政治"),
    # Malay Mail Politics
    ("https://www.malaymail.com/news/malaysia", "Malay Mail Politics", "政治"),
    # Borneo Post Nation
    ("https://www.theborneopost.com/category/national/", "Borneo Post Nation", "政治"),
    # Focus Malaysia Politics
    ("https://focusmalaysia.my/category/politics/", "Focus Malaysia Politics", "政治"),
]

# ========== 文化新闻 (Cultural News) ==========
CULTURAL_NEWS_URLS = [
    # The Star Lifestyle
    ("https://www.thestar.com.my/lifestyle", "The Star Lifestyle", "文化"),
    ("https://www.thestar.com.my/travel", "The Star Travel", "文化"),
    ("https://www.thestar.com.my/food", "The Star Food", "文化"),
    # NST Life
    ("https://www.nst.com.my/life", "NST Life", "文化"),
    ("https://www.nst.com.my/life/arts", "NST Arts", "文化"),
    # Malay Mail Life
    ("https://www.malaymail.com/news/lifestyle", "Malay Mail Lifestyle", "文化"),
    # Prestige Online
    ("https://prestige-online.com/my/", "Prestige MY", "文化"),
    # ExpatGo
    ("https://www.expatgo.com/my/", "ExpatGo Malaysia", "文化"),
    # Malaysian Digest
    ("https://malaysiandigest.com/featured/", "Malaysian Digest", "文化"),
]


def sanitize_filename(name: str) -> str:
    """Sanitize filename for safe saving"""
    return re.sub(r"[^\w\-]", "_", name)[:100]


def fetch(url: str, retries: int = 3) -> requests.Response | None:
    """Fetch URL with retry logic and better error handling"""
    for attempt in range(retries):
        try:
            # Add random delay to avoid detection
            time.sleep(DELAY + (attempt * 0.5))
            
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r
        except requests.exceptions.ConnectionError as e:
            if attempt < retries - 1:
                print(f"    [连接失败，重试 {attempt+1}/{retries}] {url}")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"  [请求失败] {url}: {e}")
                print(f"    提示：该网站可能阻止了爬虫，尝试使用备用源")
                return None
        except requests.RequestException as e:
            if attempt < retries - 1:
                print(f"    [请求错误，重试 {attempt+1}/{retries}] {url}")
                time.sleep(1)
            else:
                print(f"  [请求失败] {url}: {e}")
                return None
    
    return None


def extract_links_from_page(html_text: str, base_url: str, category: str) -> list:
    """Extract news article links from page"""
    soup = BeautifulSoup(html_text, "html.parser")
    links = []
    
    # Common patterns for news article links
    article_patterns = [
        'article', 'story', 'news', 'post', 'content'
    ]
    
    # Find all links
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text(strip=True)
        
        # Skip non-article links
        if any(skip in href.lower() for skip in [
            'login', 'register', 'subscribe', 'advertise',
            'about', 'contact', 'privacy', 'terms'
        ]):
            continue
        
        # Check if it looks like an article
        if len(text) > 20 and len(text) < 200:
            # Make absolute URL
            full_url = urljoin(base_url, href)
            
            # Skip if not from same domain
            if urlparse(full_url).netloc != urlparse(base_url).netloc:
                continue
            
            links.append({
                'title': text,
                'url': full_url,
                'category': category
            })
    
    return links[:50]  # Limit to 50 per page


def parse_article(html_text: str, url: str, category: str) -> dict:
    """Parse article page and extract content"""
    soup = BeautifulSoup(html_text, "html.parser")
    
    # Extract title
    title_el = soup.find("h1") or soup.find("title")
    title = title_el.get_text(strip=True) if title_el else "Untitled"
    
    # Extract date
    date = None
    date_patterns = ['date', 'time', 'published', 'updated']
    for pattern in date_patterns:
        date_el = soup.find(attrs={"class": re.compile(pattern, re.I)})
        if date_el:
            date = date_el.get_text(strip=True)
            break
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Extract content
    content_blocks = []
    
    # Try common content containers
    content_containers = [
        soup.find("article"),
        soup.find("div", class_=re.compile("article|content|story|post", re.I)),
        soup.find("main"),
    ]
    
    for container in content_containers:
        if container:
            for p in container.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 50 and len(text) < 1000:
                    content_blocks.append(text)
    
    # Fallback: get all paragraphs
    if not content_blocks:
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 50 and len(text) < 1000:
                content_blocks.append(text)
    
    content = "\n\n".join(content_blocks[:30])  # Limit to 30 paragraphs
    
    # Extract author if available
    author = None
    author_el = soup.find(attrs={"class": re.compile("author|byline", re.I)})
    if author_el:
        author = author_el.get_text(strip=True)
    
    return {
        'title': title,
        'url': url,
        'category': category,
        'date': date,
        'author': author,
        'content': content,
        'crawled_at': datetime.now().isoformat()
    }


def crawl_category(urls: list, category_name: str, category_cn: str):
    """Crawl news from a category"""
    print(f"\n[{category_cn}] {category_name}")
    print("=" * 60)
    
    category_dir = OUTPUT_DIR / category_name.lower()
    category_dir.mkdir(parents=True, exist_ok=True)
    
    all_articles = []
    
    for url, site_name, _ in urls:
        print(f"\n  爬取：{site_name}")
        print(f"  URL: {url}")
        
        # Fetch main page
        r = fetch(url)
        if not r:
            continue
        
        # Extract article links
        links = extract_links_from_page(r.text, url, category_name)
        print(f"  找到 {len(links)} 篇文章链接")
        
        # Fetch and parse each article
        for i, link in enumerate(links[:50], 1):
            print(f"    [{i}/{len(links)}] {link['title'][:60]}...")
            
            article_r = fetch(link['url'])
            if not article_r:
                continue
            
            article = parse_article(article_r.text, link['url'], category_name)
            
            if article['content'] and len(article['content']) > 200:
                all_articles.append(article)
                
                # Save individual article
                fname = sanitize_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{article['title'][:50]}") + ".json"
                (category_dir / fname).write_text(
                    json.dumps(article, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
        
        print(f"  ✓ 已从 {site_name} 收集 {len([a for a in all_articles if site_name in a['url']])} 篇文章")
    
    # Save summary
    summary = {
        'category': category_name,
        'category_cn': category_cn,
        'total_articles': len(all_articles),
        'crawled_at': datetime.now().isoformat(),
        'sources': [url[1] for url in urls],
        'articles': all_articles
    }
    
    summary_file = category_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary_file.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print(f"\n✓ {category_cn} 新闻收集完成!")
    print(f"  总文章数：{len(all_articles)}")
    print(f"  保存目录：{category_dir}")
    print(f"  摘要文件：{summary_file}")
    
    return all_articles


def crawl_economic_news():
    """Crawl economic news"""
    return crawl_category(ECONOMIC_NEWS_URLS, "economic", "经济")


def crawl_political_news():
    """Crawl political news"""
    return crawl_category(POLITICAL_NEWS_URLS, "political", "政治")


def crawl_cultural_news():
    """Crawl cultural news"""
    return crawl_category(CULTURAL_NEWS_URLS, "cultural", "文化")


def main():
    print("=" * 70)
    print("🇲🇾 马来西亚新闻爬虫 - Malaysian News Crawler")
    print("经济 | 政治 | 文化 - Economic | Political | Cultural")
    print("=" * 70)
    print(f"\n输出目录：{OUTPUT_DIR}\n")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    all_news = {
        'economic': [],
        'political': [],
        'cultural': []
    }
    
    # Crawl economic news
    print("\n" + "=" * 70)
    print("第一部分：经济新闻 (Economic News)")
    print("=" * 70)
    all_news['economic'] = crawl_economic_news()
    time.sleep(5)  # Longer delay between categories
    
    # Crawl political news
    print("\n" + "=" * 70)
    print("第二部分：政治新闻 (Political News)")
    print("=" * 70)
    all_news['political'] = crawl_political_news()
    time.sleep(5)
    
    # Crawl cultural news
    print("\n" + "=" * 70)
    print("第三部分：文化新闻 (Cultural News)")
    print("=" * 70)
    all_news['cultural'] = crawl_cultural_news()
    
    # Save combined summary
    total = sum(len(v) for v in all_news.values())
    combined_summary = {
        'total_articles': total,
        'by_category': {k: len(v) for k, v in all_news.items()},
        'crawled_at': datetime.now().isoformat(),
        'output_directory': str(OUTPUT_DIR)
    }
    
    combined_file = OUTPUT_DIR / f"combined_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    combined_file.write_text(
        json.dumps(combined_summary, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print("\n" + "=" * 70)
    print("✅ 爬虫完成 - Crawler Complete")
    print("=" * 70)
    print(f"\n总文章数 - Total Articles: {total}")
    print(f"  - 经济 Economic: {len(all_news['economic'])}")
    print(f"  - 政治 Political: {len(all_news['political'])}")
    print(f"  - 文化 Cultural: {len(all_news['cultural'])}")
    print(f"\n保存目录 - Output Directory: {OUTPUT_DIR}")
    print(f"摘要文件 - Summary File: {combined_file}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
