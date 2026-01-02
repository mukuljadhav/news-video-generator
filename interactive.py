#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scraper import MultiSourceScraper


def list_available_data():
    data_dir = './data'
    if not os.path.exists(data_dir):
        return []
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    return json_files


def display_menu():
    print("\n" + "="*70)
    print("🎬 NEWS VIDEO GENERATOR - Interactive Mode")
    print("="*70)
    
    data_files = list_available_data()
    
    if not data_files:
        print("\n❌ No scraped data found!")
        print("\n💡 First, scrape some data:")
        print("   python scrape_data.py --topic \"Your Topic\" --max-articles 30")
        return None
    
    print(f"\n📂 Found {len(data_files)} data file(s):\n")
    
    for i, file in enumerate(data_files, 1):
        scraper = MultiSourceScraper()
        articles = scraper.load_articles(file)
        
        topic_name = file.replace('_articles.json', '').replace('_', ' ').title()
        
        print(f"  [{i}] {topic_name}")
        print(f"      File: {file}")
        print(f"      Articles: {len(articles)}")
        print()
    
    while True:
        try:
            choice = input(f"Select data file (1-{len(data_files)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("👋 Goodbye!")
                sys.exit(0)
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(data_files):
                return data_files[choice_num - 1]
            else:
                print(f"❌ Please enter a number between 1 and {len(data_files)}")
        except ValueError:
            print("❌ Please enter a valid number")


def get_query_input():
    print("\n" + "="*70)
    print("🔍 QUERY SELECTION")
    print("="*70)
    print("\nWhat kind of summary video do you want to generate?")
    print("\nExamples:")
    print("  • positive views about [topic]")
    print("  • negative views about [topic]")
    print("  • Russia's perspective on the conflict")
    print("  • Ukraine's perspective on the conflict")
    print("  • summary of [topic]")
    print("  • achievements in [topic]")
    print("  • criticisms of [topic]")
    print()
    
    query = input("Enter your query: ").strip()
    
    if not query:
        print("❌ Query cannot be empty")
        return get_query_input()
    
    return query


def get_video_options():
    print("\n" + "="*70)
    print("⚙️  VIDEO OPTIONS")
    print("="*70)
    
    duration = input("\nVideo duration in seconds (default: 60): ").strip()
    duration = int(duration) if duration.isdigit() else 60
    
    print("\nVoice style:")
    print("  [1] Female (default)")
    print("  [2] Male")
    voice_choice = input("Select voice (1 or 2): ").strip()
    voice = "male" if voice_choice == "2" else "female"
    
    print("\nVideo quality:")
    print("  [1] Standard (faster)")
    print("  [2] Advanced with effects (slower, better quality)")
    quality_choice = input("Select quality (1 or 2): ").strip()
    advanced = quality_choice == "2"
    
    print("\nUse LLM for better analysis?")
    print("  [1] Yes (slower, better quality)")
    print("  [2] No - simple mode (faster)")
    llm_choice = input("Use LLM? (1 or 2): ").strip()
    skip_llm = llm_choice == "2"
    
    return {
        'duration': duration,
        'voice': voice,
        'advanced': advanced,
        'skip_llm': skip_llm
    }


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║               📰 NEWS VIDEO GENERATOR - Interactive                  ║
║                                                                      ║
║  Generate perspective-based summary videos from news articles       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    data_file = display_menu()
    
    if not data_file:
        return 1
    
    query = get_query_input()
    
    options = get_video_options()
    
    print("\n" + "="*70)
    print("📋 SUMMARY")
    print("="*70)
    print(f"Data file: {data_file}")
    print(f"Query: {query}")
    print(f"Duration: {options['duration']}s")
    print(f"Voice: {options['voice']}")
    print(f"Quality: {'Advanced' if options['advanced'] else 'Standard'}")
    print(f"LLM Analysis: {'Yes' if not options['skip_llm'] else 'No (simple mode)'}")
    print("="*70)
    
    confirm = input("\nGenerate video? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Cancelled")
        return 0
    
    cmd_parts = [
        "python", "generate_video.py",
        "--data", data_file,
        "--query", f'"{query}"',
        "--duration", str(options['duration']),
        "--voice", options['voice']
    ]
    
    if options['advanced']:
        cmd_parts.append("--advanced")
    
    if options['skip_llm']:
        cmd_parts.append("--skip-llm")
    
    cmd = " ".join(cmd_parts)
    
    print(f"\n🚀 Executing: {cmd}\n")
    
    os.system(cmd)
    
    print("\n" + "="*70)
    print("✅ Done! Check the output/ directory for your video.")
    print("="*70)
    
    another = input("\nGenerate another video from the same or different data? (y/n): ").strip().lower()
    
    if another == 'y':
        print("\n" + "="*70)
        main()
    else:
        print("\n👋 Thank you for using News Video Generator!")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
