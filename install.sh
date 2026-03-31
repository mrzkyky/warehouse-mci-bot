#!/bin/bash
# Warehouse Bot Installer for Linux/Mac

set -e

echo "=========================================="
echo "WAREHOUSE BOT - INSTALLER"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo -e "${RED}[X] Python not found!${NC}"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python: $($PYTHON --version)"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p data reports temp
echo -e "${GREEN}[OK]${NC} Directories ready"

# Install dependencies
echo ""
echo "Installing dependencies... (may take a few minutes)"
$PYTHON -m pip install -q -r requirements.txt
echo -e "${GREEN}[OK]${NC} Dependencies installed"

# Setup .env
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}[!] IMPORTANT:${NC} Edit .env with your BOT_TOKEN from @BotFather"
else
    echo -e "${GREEN}[OK]${NC} .env already exists"
fi

# Check Tesseract
echo ""
echo "Checking Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Tesseract: $(tesseract --version | head -1)"
else
    echo -e "${YELLOW}[!]${NC} Tesseract not found"
    echo "    Install: sudo apt install tesseract-ocr"
    echo "    (Optional - only needed for SN scanning feature)"
fi

# Test parser
echo ""
echo "Testing parser..."
$PYTHON demo.py

# Done
echo ""
echo "=========================================="
echo -e "${GREEN}INSTALLATION COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your BOT_TOKEN (from @BotFather)"
echo "2. Get your Telegram ID from @userinfobot"
echo "3. Add your ID to ADMIN_IDS in .env"
echo "4. Run: python bot.py"
echo ""
echo "Or with Docker:"
echo "   docker-compose up -d"
echo ""
