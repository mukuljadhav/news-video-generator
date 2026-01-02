# News Video Generator

Generate perspective-based summary videos from news articles using **100% open-source models**. No API keys required!

## 🎯 Key Concept

**Two-Step Process:**
1. **Scrape data first** - Collect news articles on any topic
2. **Generate multiple videos** - Create different perspective summaries from the same data

This allows you to generate both positive and negative views (or any perspective) from the same source data - **no hallucinations**, only facts from articles.

## ⚡ Quick Start

### Step 1: Scrape News Data

```bash
# Scrape Ukraine articles (extracts full article content ~5K chars each)
python scrape_news.py --topic "Ukraine" --max-articles 15 --output data/ukraine_news.json

# More examples:
# China news
python scrape_news.py --topic "China" --max-articles 20 --output data/china_news.json

# India news
python scrape_news.py --topic "India" --max-articles 15 --output data/india_news.json

# Tesla news
python scrape_news.py --topic "Tesla" --max-articles 15 --output data/tesla_news.json
```

**Why this scraper?**
- ✅ Extracts **full article content** (3,000-9,000 chars per article)
- ✅ Uses BBC RSS feeds (reliable, no paywalls)
- ✅ Much better LLM summaries due to complete context
- ❌ Legacy scrapers only get 50-200 char RSS summaries

### Step 2: Generate Summary Videos

From the **same scraped data**, generate different perspectives:

```bash
# Overall summary of Ukraine news
python generate_video.py \
  --data data/ukraine_news.json \
  --query "summary of Ukraine news" \
  --duration 60

# Peace negotiations focus
python generate_video.py \
  --data data/ukraine_news.json \
  --query "progress on Ukraine-Russia peace negotiations" \
  --duration 60

# Ukraine's perspective
python generate_video.py \
  --data data/ukraine_news.json \
  --query "Ukraine's perspective on the peace deal" \
  --duration 60

# Russia's perspective
python generate_video.py \
  --data data/ukraine_news.json \
  --query "Russia's perspective on the conflict" \
  --duration 60
```

### Or Use Interactive Mode

```bash
python interactive.py
```

The interactive mode will:
- Show all available scraped data
- Let you select which dataset to use
- Ask for your query (e.g., "positive views", "peace negotiations")
- Configure video options
- Generate the video

## 📦 Installation

### Prerequisites

- Python 3.9+
- FFmpeg (required for video generation)
- 8GB+ RAM (16GB recommended for LLM)
- GPU optional (speeds up LLM inference)

### Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

### Install Python Dependencies

```bash
cd news-video-generator
./install.sh
```

Or manually:
```bash
pip install -r requirements.txt
```

## 🎬 Complete Workflow Examples

### Example 1: Ukraine News - Multiple Perspectives

```bash
# Step 1: Scrape data once (gets 3 articles, ~15K chars total)
python scrape_news.py --topic "Ukraine" --max-articles 15 --output data/ukraine_news.json

# Step 2: Generate multiple videos from same data
python generate_video.py --data data/ukraine_news.json --query "summary of Ukraine news" --duration 60
python generate_video.py --data data/ukraine_news.json --query "Ukraine's perspective on peace negotiations" --duration 60
python generate_video.py --data data/ukraine_news.json --query "Russia's perspective on the conflict" --duration 90
```

### Example 2: China News

```bash
# Step 1: Scrape data (3 articles available)
python scrape_news.py --topic "China" --max-articles 20 --output data/china_news.json

# Step 2: Generate videos
python generate_video.py --data data/china_news.json --query "summary of China news" --duration 60
python generate_video.py --data data/china_news.json --query "China's economic developments" --duration 75
```

### Example 3: India News

```bash
# Step 1: Scrape (2 articles available)
python scrape_news.py --topic "India" --max-articles 15 --output data/india_news.json

# Step 2: Generate videos
python generate_video.py --data data/india_news.json --query "summary of India news" --duration 60
python generate_video.py --data data/india_news.json --query "India's political landscape" --duration 75
```

## 🛠️ Advanced Options

### Scraping Options

```bash
python scrape_news.py --topic "Your Topic" --max-articles 20 --output data/custom_filename.json
```

### Video Generation Options

```bash
python generate_video.py \
  --data your_articles.json \
  --query "your query" \
  --duration 90 \
  --voice male \
  --advanced \
  --use-quantized \
  --output my_video.mp4
```

**Options:**
- `--voice male|female` - Voice style
- `--advanced` - Professional video with effects (slower)
- `--use-quantized` - Lower memory usage for LLM
- `--skip-llm` - Fast mode without LLM (lower quality)
- `--output` - Custom output filename

## 📂 Project Structure

```
news-video-generator/
├── generate_video.py       # Generate videos from scraped data
├── scrape_news.py          # Scrape news articles (easy CLI)
├── interactive.py          # Interactive mode UI
├── src/
│   ├── news_scraper.py     # Full-content BBC RSS scraper (RECOMMENDED)
│   ├── scraper.py          # Legacy multi-source scraper
│   ├── content_analyzer.py # LLM-based summary generation
│   ├── tts_generator.py    # Text-to-speech (Coqui TTS)
│   ├── image_fetcher.py    # Background image fetching
│   └── video_creator.py    # Video assembly (MoviePy)
├── data/                   # Scraped articles (cached)
├── output/                 # Generated videos
└── requirements.txt
```

## 🔑 Key Features

✅ **No Hallucinations** - Only uses facts from scraped articles  
✅ **Multiple Perspectives** - Generate different views from same data  
✅ **100% Open Source** - Mistral-7B LLM, Coqui TTS, MoviePy  
✅ **No API Keys** - Completely free  
✅ **Multi-Source Scraping** - BBC, Reuters, Google News, RSS feeds  
✅ **Professional Videos** - Synchronized audio, images, captions  
✅ **Interactive Mode** - Easy-to-use interface  

## 🧠 How It Works

1. **Scraping**: Fetches articles from multiple news sources (BBC, Reuters, etc.)
2. **Storage**: Saves articles as JSON for reuse
3. **Analysis**: LLM (Mistral-7B) analyzes articles based on your query
4. **Filtering**: Extracts only relevant content matching your perspective
5. **Script Generation**: Creates a coherent summary script
6. **Speech Synthesis**: Converts script to natural voice (Coqui TTS)
7. **Image Fetching**: Finds relevant background images
8. **Video Assembly**: Combines everything into a professional video

## 🎯 Use Cases

- **Media Analysis**: Compare positive vs negative coverage
- **Perspective Comparison**: Different viewpoints on same event
- **Content Summarization**: Quick video summaries of news
- **Educational**: Show how same facts can be presented differently
- **Research**: Analyze media bias and framing

## 🚀 Performance

- **First Run**: 10-15 minutes (downloads models ~2-3GB)
- **Subsequent Runs**: 3-5 minutes per video
- **With GPU**: 2-3 minutes per video
- **Fast Mode (--skip-llm)**: 1-2 minutes per video

## 🐛 Troubleshooting

### No Articles Found
- Use broader search terms
- Check internet connection
- Try different topic keywords

### LLM Out of Memory
```bash
python generate_video.py --data file.json --query "your query" --use-quantized
```

### Very Slow Generation
```bash
python generate_video.py --data file.json --query "your query" --skip-llm
```

### FFmpeg Not Found
Make sure FFmpeg is installed and in PATH. Test with: `ffmpeg -version`

## 📚 More Examples

See `EXAMPLES.md` for comprehensive usage examples and tips.

## 🤝 Contributing

Contributions welcome! This is a fully open-source project.

## 📄 License

MIT License - Free for personal and commercial use

## 🙏 Acknowledgments

- **Mistral AI** - Open-source LLM
- **Coqui TTS** - Open-source speech synthesis
- **MoviePy** - Video editing library
- **News organizations** - For public content access
