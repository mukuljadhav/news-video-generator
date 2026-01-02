import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict
from datetime import datetime
import feedparser
from urllib.parse import urljoin, urlparse
import re


class NewsArticle:
    def __init__(self, title: str, content: str, url: str, source: str, published_date: str = None):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.published_date = published_date or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'published_date': self.published_date
        }


class MultiSourceScraper:
    def __init__(self, cache_dir: str = './data'):
        self.cache_dir = cache_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_topic(self, topic: str, max_articles: int = 20) -> List[NewsArticle]:
        articles = []
        
        print(f"🔍 Scraping articles about: {topic}")
        
        articles.extend(self._scrape_rss_feeds(topic, max_articles))
        
        articles = articles[:max_articles]
        print(f"✅ Found {len(articles)} articles")
        
        return articles
    
    def _scrape_rss_feeds(self, topic: str, max_articles: int) -> List[NewsArticle]:
        articles = []
        rss_feeds = [
            'http://feeds.bbci.co.uk/news/rss.xml',
            'https://feeds.reuters.com/reuters/topNews',
            'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
            'https://www.theguardian.com/world/rss',
        ]
        
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:max_articles]:
                    title_str = str(entry.title) if hasattr(entry, 'title') else ''
                    summary_str = str(entry.get('summary', ''))
                    
                    if topic.lower() in title_str.lower() or topic.lower() in summary_str.lower():
                        full_content = self._extract_article_content(entry.link)
                        
                        if not full_content or len(full_content) < 200:
                            full_content = BeautifulSoup(summary_str, 'html.parser').get_text()
                        
                        article = NewsArticle(
                            title=title_str,
                            content=full_content,
                            url=entry.link,
                            source=urlparse(feed_url).netloc,
                            published_date=str(entry.get('published', ''))
                        )
                        articles.append(article)
                        
                        if len(articles) >= max_articles:
                            break
                
                time.sleep(1)
            except Exception as e:
                print(f"⚠️  Error scraping RSS feed {feed_url}: {e}")
                continue
        
        return articles
    
    def _extract_article_content(self, url: str) -> str:
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'button', 'form']):
                tag.decompose()
            
            paragraphs = []
            article_body = soup.find_all('p')
            if article_body:
                paragraphs = [p.get_text().strip() for p in article_body if p.get_text().strip() and len(p.get_text().strip()) > 40]
            
            content = " ".join(paragraphs)
            
            if len(content) > 300:
                return content
            
            return ''
        
        except Exception as e:
            print(f"   ⚠️  Error extracting content from {url[:50]}...: {e}")
            return ''
    
    def _scrape_google_news(self, topic: str, max_articles: int) -> List[NewsArticle]:
        articles = []
        
        try:
            search_url = f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(search_url)
            
            for entry in feed.entries[:max_articles]:
                full_content = self._extract_article_content(entry.link)
                
                if not full_content or len(full_content) < 200:
                    content = entry.get('summary', '') or entry.get('description', '')
                    full_content = BeautifulSoup(content, 'html.parser').get_text()
                
                article = NewsArticle(
                    title=entry.title,
                    content=full_content,
                    url=entry.link,
                    source='Google News',
                    published_date=entry.get('published', '')
                )
                articles.append(article)
                time.sleep(1)
        
        except Exception as e:
            print(f"⚠️  Error scraping Google News: {e}")
        
        return articles
    
    def _scrape_reuters(self, topic: str, max_articles: int) -> List[NewsArticle]:
        articles = []
        
        try:
            search_url = f"https://www.reuters.com/site-search/?query={topic.replace(' ', '%20')}"
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            article_links = soup.find_all('a', {'data-testid': 'Heading'}, limit=max_articles)
            
            for link in article_links[:max_articles]:
                try:
                    article_url = urljoin('https://www.reuters.com', link.get('href'))
                    article_response = self.session.get(article_url, timeout=10)
                    article_soup = BeautifulSoup(article_response.content, 'html.parser')
                    
                    title = article_soup.find('h1')
                    title = title.get_text(strip=True) if title else link.get_text(strip=True)
                    
                    paragraphs = article_soup.find_all('p', {'data-testid': 'paragraph-0'})
                    if not paragraphs:
                        paragraphs = article_soup.find_all('p')
                    
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])
                    
                    if content:
                        article = NewsArticle(
                            title=title,
                            content=content,
                            url=article_url,
                            source='Reuters'
                        )
                        articles.append(article)
                    
                    time.sleep(2)
                
                except Exception as e:
                    print(f"⚠️  Error scraping Reuters article: {e}")
                    continue
        
        except Exception as e:
            print(f"⚠️  Error accessing Reuters: {e}")
        
        return articles
    
    def _scrape_bbc(self, topic: str, max_articles: int) -> List[NewsArticle]:
        articles = []
        
        try:
            search_url = f"https://www.bbc.com/search?q={topic.replace(' ', '+')}"
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            article_links = soup.find_all('a', {'class': re.compile('ssrcss.*')}, limit=max_articles * 2)
            
            seen_urls = set()
            for link in article_links:
                if len(articles) >= max_articles:
                    break
                
                href = link.get('href')
                if not href or '/news/' not in href:
                    continue
                
                article_url = urljoin('https://www.bbc.com', href)
                
                if article_url in seen_urls:
                    continue
                seen_urls.add(article_url)
                
                try:
                    article_response = self.session.get(article_url, timeout=10)
                    article_soup = BeautifulSoup(article_response.content, 'html.parser')
                    
                    title = article_soup.find('h1')
                    if not title:
                        continue
                    title = title.get_text(strip=True)
                    
                    article_body = article_soup.find('article')
                    if article_body:
                        paragraphs = article_body.find_all('p')
                    else:
                        paragraphs = article_soup.find_all('p', {'data-component': 'text-block'})
                    
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])
                    
                    if content and len(content) > 100:
                        article = NewsArticle(
                            title=title,
                            content=content,
                            url=article_url,
                            source='BBC'
                        )
                        articles.append(article)
                    
                    time.sleep(2)
                
                except Exception as e:
                    print(f"⚠️  Error scraping BBC article: {e}")
                    continue
        
        except Exception as e:
            print(f"⚠️  Error accessing BBC: {e}")
        
        return articles
    
    def save_articles(self, articles: List[NewsArticle], filename: str):
        import os
        os.makedirs(self.cache_dir, exist_ok=True)
        
        filepath = os.path.join(self.cache_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([article.to_dict() for article in articles], f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(articles)} articles to {filepath}")
    
    def load_articles(self, filename: str) -> List[NewsArticle]:
        import os
        filepath = os.path.join(self.cache_dir, filename)
        
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles = [
            NewsArticle(
                title=item['title'],
                content=item['content'],
                url=item['url'],
                source=item['source'],
                published_date=item.get('published_date')
            ) for item in data
        ]
        
        print(f"📂 Loaded {len(articles)} articles from cache")
        return articles


if __name__ == "__main__":
    scraper = MultiSourceScraper()
    articles = scraper.scrape_topic("Elon Musk", max_articles=10)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.title}")
        print(f"   Source: {article.source}")
        print(f"   Content preview: {article.content[:200]}...")
    
    scraper.save_articles(articles, "elon_musk_articles.json")
