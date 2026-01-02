import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time
from typing import List, Dict
import feedparser
from tqdm import tqdm
from dateutil import parser as date_parser


class NewsScraper:
    def __init__(self):
        self.rss_feeds = [
            "http://feeds.bbci.co.uk/news/rss.xml",
            "http://feeds.bbci.co.uk/news/technology/rss.xml",
            "http://feeds.bbci.co.uk/news/business/rss.xml",
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        ]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def scrape_topic(self, topic: str, max_articles: int = 20, days_back: int = 7) -> List[Dict]:
        cutoff_date = datetime.now() - timedelta(days=days_back)
        articles = []
        seen_urls = set()

        print(f"🔍 Scraping articles about: {topic}")

        for feed_url in tqdm(self.rss_feeds, desc="Processing RSS feeds"):
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    try:
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                            published = datetime(*entry.updated_parsed[:6])
                        elif hasattr(entry, 'published'):
                            published = date_parser.parse(entry.published)
                        else:
                            published = datetime.now()
                    except (TypeError, ValueError, AttributeError):
                        published = datetime.now()

                    title_lower = entry.title.lower() if hasattr(entry, 'title') else ''
                    summary_lower = entry.get("summary", "").lower() if entry.get("summary") else ''
                    
                    if (published >= cutoff_date and 
                        entry.link not in seen_urls and
                        (topic.lower() in title_lower or topic.lower() in summary_lower)):
                        
                        article = {
                            "url": entry.link,
                            "title": entry.title,
                            "published_date": published.isoformat(),
                            "summary": entry.get("summary", ""),
                            "source": feed_url.split('/')[2],
                        }
                        articles.append(article)
                        seen_urls.add(entry.link)
                        
                        if len(articles) >= max_articles:
                            break

                time.sleep(0.5)

            except Exception as e:
                print(f"⚠️  Error processing feed {feed_url}: {e}")
                continue
            
            if len(articles) >= max_articles:
                break

        print(f"📰 Found {len(articles)} articles from RSS feeds")
        return articles

    def scrape_article_content(self, url: str) -> Dict:
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            paragraphs = []
            article_body = soup.find_all("p")
            if article_body:
                paragraphs = [p.get_text().strip() for p in article_body if p.get_text().strip() and len(p.get_text().strip()) > 40]

            content = " ".join(paragraphs)

            return {"content": content, "success": True}

        except Exception as e:
            return {"content": "", "success": False, "error": str(e)}

    def scrape_full_articles(self, articles: List[Dict]) -> List[Dict]:
        print(f"\n📥 Fetching full content for {len(articles)} articles...")
        full_articles = []

        for article in tqdm(articles, desc="Scraping content"):
            content_data = self.scrape_article_content(article["url"])

            if content_data["success"] and content_data["content"]:
                article["content"] = content_data["content"]
            else:
                article["content"] = article.get("summary", "")

            full_articles.append(article)
            time.sleep(2)

        successful = sum(1 for a in full_articles if len(a.get("content", "")) > 500)
        print(f"✅ Successfully scraped {successful}/{len(full_articles)} articles with full content")
        
        return full_articles

    def save_to_json(self, articles: List[Dict], filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(articles)} articles to {filename}")

    def run(self, topic: str, max_articles: int = 20, output_file: str = ""):
        if not output_file:
            safe_topic = topic.lower().replace(' ', '_')
            output_file = f"data/{safe_topic}_articles.json"

        articles = self.scrape_topic(topic, max_articles)
        
        if len(articles) > 0:
            full_articles = self.scrape_full_articles(articles)
        else:
            full_articles = []
            print("⚠️  No articles found matching the topic")

        self.save_to_json(full_articles, output_file)

        return full_articles


if __name__ == "__main__":
    scraper = NewsScraper()
    articles = scraper.run(topic="Elon Musk", max_articles=15)
    
    for i, article in enumerate(articles[:3], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Content length: {len(article.get('content', ''))} chars")
        print(f"   Content preview: {article.get('content', '')[:200]}...")
