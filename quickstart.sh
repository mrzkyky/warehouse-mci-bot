#!/bin/bash
# Quick start script for Warehouse Bot

set -e

echo "🚀 Warehouse Bot Quick Start"
echo "=============================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check Tesseract
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found!"
    echo "   Install with: sudo apt install tesseract-ocr"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Tesseract found: $(tesseract --version | head -1)"
fi

# Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p data reports temp
echo "✅ Directories created"

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
echo ""
echo "⏳ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your BOT_TOKEN!"
    echo "   Get token from @BotFather on Telegram"
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python3 -c "from models import init_db; init_db()"
echo "✅ Database ready"

# Test parser
echo ""
echo "🧪 Testing parser..."
python3 test_parser.py > /dev/null 2>&1 && echo "✅ Parser OK" || echo "⚠️  Parser test had issues"

echo ""
echo "=============================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your BOT_TOKEN"
echo "2. Run: python bot.py"
echo ""
echo "Or use Docker: docker-compose up -d"
echo "=============================="
