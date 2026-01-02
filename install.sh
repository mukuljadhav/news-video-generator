#!/bin/bash

echo "================================================"
echo "News Video Generator - Installation Script"
echo "================================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python version: $PYTHON_VERSION"

if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo "⚠️  FFmpeg is not installed!"
    echo "   Please install FFmpeg:"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu: sudo apt install ffmpeg"
    echo "   - Windows: Download from https://ffmpeg.org/download.html"
    echo ""
    read -p "Continue without FFmpeg? Video generation will fail. (y/N): " continue_install
    if [[ ! $continue_install =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ Found FFmpeg"
fi

echo ""
echo "📦 Installing Python dependencies..."
echo "   This may take 5-10 minutes on first run..."
echo ""

pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "✅ Installation Complete!"
    echo "================================================"
    echo ""
    echo "Quick Start:"
    echo "  python3 main.py --topic \"Elon Musk\" --perspective \"positive views\" --duration 60"
    echo ""
    echo "For more examples, see README.md"
    echo ""
else
    echo ""
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
