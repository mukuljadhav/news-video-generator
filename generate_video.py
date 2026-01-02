import argparse
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scraper import MultiSourceScraper
from src.content_analyzer import ContentAnalyzer
from src.tts_generator import TTSGenerator, AdvancedTTSGenerator
from src.image_fetcher import ImageFetcher
from src.video_creator import VideoCreator, AdvancedVideoCreator


def main():
    parser = argparse.ArgumentParser(
        description='Generate summary videos from pre-scraped news data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
WORKFLOW:
  1. First, scrape data: python scrape_data.py --topic "Elon Musk"
  2. Then, generate videos: python generate_video.py --data elon_musk_articles.json --query "positive views"

Examples:
  # Summary of positive views about Elon Musk
  python generate_video.py --data elon_musk_articles.json --query "positive views about Elon Musk" --duration 60
  
  # Summary of negative views
  python generate_video.py --data elon_musk_articles.json --query "negative views about Elon Musk" --duration 60
  
  # Summary from Russia's perspective
  python generate_video.py --data russia_ukraine_war_articles.json --query "Russia's perspective on the conflict" --duration 90
  
  # Summary from Ukraine's perspective
  python generate_video.py --data russia_ukraine_war_articles.json --query "Ukraine's perspective on the conflict" --duration 90
  
  # General summary
  python generate_video.py --data climate_change_articles.json --query "summary of climate change" --duration 120
        """
    )
    
    parser.add_argument('--data', type=str, required=True,
                       help='Pre-scraped data file (e.g., elon_musk_articles.json)')
    parser.add_argument('--query', type=str, required=True,
                       help='Query for summary generation (e.g., "positive views about Elon Musk", "Russia\'s perspective")')
    parser.add_argument('--duration', type=int, default=60,
                       help='Target video duration in seconds (default: 60)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output video filename (default: auto-generated)')
    parser.add_argument('--voice', type=str, choices=['male', 'female'], default='female',
                       help='TTS voice style (default: female)')
    parser.add_argument('--use-quantized', action='store_true',
                       help='Use quantized model for lower memory usage')
    parser.add_argument('--skip-llm', action='store_true',
                       help='Skip LLM analysis and use simple script generation (faster, lower quality)')
    parser.add_argument('--advanced', action='store_true',
                       help='Use advanced video creation with effects')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🎥 NEWS VIDEO GENERATOR - Summary Mode")
    print("="*70)
    print(f"Data File: {args.data}")
    print(f"Query: {args.query}")
    print(f"Duration: {args.duration}s")
    print("="*70 + "\n")
    
    scraper = MultiSourceScraper()
    
    data_path = args.data if args.data.startswith('data/') else f"data/{args.data}"
    
    if not os.path.exists(data_path):
        print(f"❌ Data file not found: {data_path}")
        print("\n💡 First scrape data using:")
        print(f"   python scrape_data.py --topic \"Your Topic\"")
        return 1
    
    print(f"📂 Loading pre-scraped data from: {data_path}")
    articles = scraper.load_articles(os.path.basename(data_path))
    
    if not articles:
        print("❌ No articles found in data file")
        return 1
    
    print(f"✅ Loaded {len(articles)} articles\n")
    
    articles_dict = [article.to_dict() for article in articles]
    
    if args.skip_llm:
        print("⚡ Using simple script generation (no LLM)...")
        script = generate_simple_script(articles_dict, args.query, args.duration)
        keywords = extract_keywords_simple(args.query)
    else:
        print("🤖 Analyzing content with LLM to generate summary...")
        try:
            analyzer = ContentAnalyzer(use_quantized=args.use_quantized)
            
            analysis = analyzer.analyze_articles(articles_dict, args.query, max_tokens=1500)
            
            script = analysis.get('script', '')
            keywords = analysis.get('search_keywords', [])
            
            if not script or len(script) < 100:
                print("⚠️  LLM generated insufficient content, using enhanced fallback...")
                script = generate_comprehensive_script(articles_dict, args.query, args.duration)
        
        except Exception as e:
            print(f"⚠️  LLM analysis failed: {e}")
            print("   Falling back to simple script generation...")
            script = generate_simple_script(articles_dict, args.query, args.duration)
            keywords = extract_keywords_simple(args.query)
    
    print(f"\n📝 Generated Summary Script:")
    print(f"   Length: {len(script)} characters, {len(script.split())} words")
    print(f"   Preview: {script[:200]}...")
    
    tts_generator = AdvancedTTSGenerator(voice_style=args.voice) if not args.skip_llm else TTSGenerator(voice_style=args.voice)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"audio_{timestamp}.wav"
    audio_path = os.path.join("./output", audio_filename)
    tts_generator.generate_speech(script, audio_path)
    
    image_fetcher = ImageFetcher()
    num_images = max(5, args.duration // 12)
    
    if not keywords:
        keywords = extract_keywords_simple(args.query)
    
    image_paths = image_fetcher.fetch_images(keywords, num_images=num_images)
    
    if args.output:
        output_filename = args.output if args.output.endswith('.mp4') else f"{args.output}.mp4"
    else:
        query_clean = args.query.replace(' ', '_').lower()[:40]
        output_filename = f"summary_{query_clean}_{timestamp}.mp4"
    
    if args.advanced:
        video_creator = AdvancedVideoCreator()
        video_path = video_creator.create_professional_video(
            script=script,
            audio_path=audio_path,
            image_paths=image_paths,
            output_filename=output_filename,
            title_text=f"Summary: {args.query}"
        )
    else:
        video_creator = VideoCreator()
        video_path = video_creator.create_video(
            script=script,
            audio_path=audio_path,
            image_paths=image_paths,
            output_filename=output_filename,
            title_text=None
        )
    
    print("\n" + "="*70)
    print("✨ VIDEO GENERATION COMPLETE!")
    print("="*70)
    print(f"📹 Video: {video_path}")
    print(f"🎵 Audio: {audio_path}")
    print(f"📊 Articles used: {len(articles)}")
    print(f"🔍 Query: {args.query}")
    print("="*70)
    
    print("\n💡 Generate another perspective from the same data:")
    print(f"   python generate_video.py --data {args.data} --query \"different query\" --duration {args.duration}")
    print()
    
    return 0


def generate_comprehensive_script(articles, query, target_duration):
    titles = [article['title'] for article in articles if article.get('title')]
    
    intro = f"In recent news about {query}, here are the key developments. "
    
    summaries = []
    for i, title in enumerate(titles[:12], 1):
        summaries.append(f"{title}.")
    
    script = intro + " ".join(summaries)
    
    words_per_second = 2.5
    target_words = int(target_duration * words_per_second)
    words = script.split()
    
    if len(words) > target_words:
        script = " ".join(words[:target_words])
    
    return script


def generate_simple_script(articles, query, target_duration):
    combined_content = []
    
    query_lower = query.lower()
    
    for article in articles:
        article_text = f"{article['title']}. {article['content']}"
        
        if 'positive' in query_lower:
            positive_words = ['success', 'achievement', 'growth', 'innovation', 'praised', 'optimistic', 'support', 'benefit', 'improve']
            if any(word in article_text.lower() for word in positive_words):
                combined_content.append(article_text[:400])
        elif 'negative' in query_lower:
            negative_words = ['concern', 'criticism', 'problem', 'controversy', 'decline', 'risk', 'challenge', 'oppose', 'fail']
            if any(word in article_text.lower() for word in negative_words):
                combined_content.append(article_text[:400])
        else:
            combined_content.append(article_text[:400])
    
    if not combined_content:
        for article in articles[:10]:
            combined_content.append(f"{article['title']}. {article['content'][:300]}")
    
    full_text = " ".join(combined_content[:15])
    
    target_words = int(target_duration * 2.5)
    
    words = full_text.split()[:target_words]
    
    script = " ".join(words)
    
    return script


def extract_keywords_simple(query):
    keywords = query.split()
    
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'summary', 'views', 'perspective'}
    keywords = [k for k in keywords if k.lower() not in common_words]
    
    return keywords[:5]


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
