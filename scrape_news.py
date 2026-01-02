import argparse
import sys
from src.news_scraper import NewsScraper


def main():
    parser = argparse.ArgumentParser(
        description='Scrape news articles from various sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape Ukraine news
  python scrape_news.py --topic "Ukraine" --max-articles 15 --output data/ukraine_news.json
  
  # Scrape Elon Musk news
  python scrape_news.py --topic "Elon Musk" --max-articles 20 --output data/elon_musk_news.json
  
  # Scrape climate change news
  python scrape_news.py --topic "climate change" --max-articles 30 --output data/climate_news.json
        """
    )
    
    parser.add_argument('--topic', type=str, required=True,
                       help='Topic to search for (e.g., "Ukraine", "Elon Musk")')
    parser.add_argument('--max-articles', type=int, default=15,
                       help='Maximum number of articles to scrape (default: 15)')
    parser.add_argument('--output', type=str, default='data/news.json',
                       help='Output JSON file path (default: data/news.json)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("📰 NEWS SCRAPER")
    print("="*70)
    print(f"Topic: {args.topic}")
    print(f"Max Articles: {args.max_articles}")
    print(f"Output: {args.output}")
    print("="*70 + "\n")
    
    try:
        scraper = NewsScraper()
        scraper.run(
            topic=args.topic,
            max_articles=args.max_articles,
            output_file=args.output
        )
        
        print("\n" + "="*70)
        print("✅ SCRAPING COMPLETE!")
        print("="*70)
        print(f"📁 Saved to: {args.output}")
        print("\n💡 Next step: Generate a video from this data:")
        print(f"   python generate_video.py --data {args.output} --query \"summary of {args.topic}\" --duration 60")
        print("="*70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
