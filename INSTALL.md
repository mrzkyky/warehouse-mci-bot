# Installation Guide

## Prerequisites

- Python 3.9+ (recommended: 3.11)
- Tesseract OCR 4.x+
- (Optional) Docker & Docker Compose

## Method 1: Docker (Recommended for Production)

### Step 1: Install Docker

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

**Windows:**
Download [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Step 2: Get Bot Token

1. Buka Telegram, cari [@BotFather](https://t.me/botfather)
2. Kirim `/newbot`
3. Ikuti instruksi, simpan token yang diberikan

### Step 3: Clone & Setup

```bash
# Clone repository (atau copy files)
git clone <your-repo> warehouse-bot
cd warehouse-bot

# Copy environment file
cp .env.example .env

# Edit .env
nano .env  # atau notepad .env
```

Edit `.env`:
```env
BOT_TOKEN=your_token_here
ADMIN_IDS=your_telegram_user_id
```

Cari user ID Telegram dengan bot [@userinfobot](https://t.me/userinfobot)

### Step 4: Run

```bash
docker-compose up -d
```

Check logs:
```bash
docker-compose logs -f bot
```

Stop:
```bash
docker-compose down
```

## Method 2: Native Python

### Step 1: Install Python & Tesseract

**Ubuntu/Debian:**
```bash
# Python (usually pre-installed)
python3 --version

# Tesseract OCR
sudo apt update
sudo apt install -y tesseract-ocr libtesseract-dev

# Verify
tesseract --version
```

**Windows:**
1. Download Python dari [python.org](https://python.org)
2. Download Tesseract dari [github](https://github.com/UB-Mannheim/tesseract/wiki)
3. Install keduanya, tambahkan ke PATH

**macOS:**
```bash
brew install tesseract
```

### Step 2: Setup Project

```bash
# Clone/copy files
cd warehouse-bot

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup
python setup.py
```

### Step 3: Configure

Edit `.env` dengan token bot dan admin IDs.

### Step 4: Run

```bash
python bot.py
```

## Verification

1. Buka Telegram
2. Cari bot kamu
3. Kirim `/start`
4. Bot harus reply dengan menu

## Troubleshooting

### "tesseract not found"

**Windows:**
- Pastikan Tesseract di PATH
- Atau edit `.env`:
  ```
  TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
  ```

**Linux:**
```bash
which tesseract
# Jika tidak ketemu:
sudo apt install tesseract-ocr
```

### "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### Bot tidak respon

1. Check token benar (dari @BotFather)
2. Check bot tidak di-block
3. Check logs: `docker-compose logs` atau console output
4. Coba restart: `docker-compose restart`

### Database errors

SQLite (default) should work out of the box.

Untuk PostgreSQL:
```yaml
# docker-compose.yml - uncomment db service
# Edit .env:
DATABASE_URL=postgresql://warehouse:password@db:5432/warehouse
```

## Production Checklist

- [ ] Gunakan PostgreSQL, bukan SQLite
- [ ] Set webhook mode (lebih scalable)
- [ ] Setup backup otomatis
- [ ] Monitoring (health checks)
- [ ] Log rotation
- [ ] Firewall rules

## Upgrade

```bash
# Docker
docker-compose down
docker-compose pull  # if using prebuilt image
docker-compose up -d

# Native
git pull
pip install -r requirements.txt
python bot.py
```

## Uninstall

```bash
# Docker
docker-compose down -v
rm -rf warehouse-bot

# Native
deactivate  # exit venv
rm -rf venv
rm -rf warehouse-bot
```
