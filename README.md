# Warehouse Telegram Bot 🤖📦

Bot Telegram untuk pencatatan barang gudang (masuk, keluar, stock opname) dengan fitur OCR untuk scan Serial Number.

## Features

- ✅ **Chat-based Input** - Kirim pesan natural language
- ✅ **OCR Serial Number** - Scan SN dari foto label barang
- ✅ **Daily Report** - Generate laporan harian otomatis
- ✅ **Multi Format** - Text, Excel export
- ✅ **Stock Opname** - Format SO sesuai contoh

## Quick Start

### 1. Clone & Setup

```bash
cd warehouse-bot
cp .env.example .env
```

### 2. Edit `.env`

```env
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_IDS=your_telegram_id
```

Dapatkan BOT_TOKEN dari [@BotFather](https://t.me/botfather)

### 3. Run dengan Docker (Recommended)

```bash
docker-compose up -d
```

### 4. Atau Run Manual

```bash
# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# Ubuntu/Debian:
sudo apt install tesseract-ocr libtesseract-dev

# Windows: Download dari https://github.com/UB-Mannheim/tesseract/wiki

# Run
python bot.py
```

## Usage

### Format Pesan

**Barang Keluar:**
```
Kebutuhan migrasi server unit JTB
- DCDU 12B huawei (1 unit)
SN: 21021207316TL4922814
- batterai ZTE ZXDC48 FB100B3 (1 unit)
SN: 219502212702
```

**Barang Masuk:**
```
sisaan BOQ jatibarang > rajak
- tiang 3inch 7m Biasa (25 Btg)
```

**Stock Opname:**
```
SO 15 Maret 2026

∆Data Sfp
SFP MultiMode (MM)
•Huawei 155Mbps 15Km 1310 Nm (2pcs)
•Fiberson 1G 550M 850Nm (1pcs)
```

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Start bot & show menu |
| `/rekap` | Generate laporan hari ini |
| `/scan` | Scan SN dari foto |
| `/help` | Show help |
| `/batal` | Cancel current operation |

### Chat Commands

- Ketik `rekap` atau "laporan" untuk generate report
- Kirim foto untuk OCR otomatis
- Bot akan minta konfirmasi sebelum menyimpan

## Architecture

```
warehouse-bot/
├── bot.py              # Main Telegram bot
├── parser.py           # NLP message parser
├── ocr.py              # OCR for SN extraction
├── report_generator.py # Report generation
├── models.py           # Database models
├── config.py           # Configuration
├── requirements.txt    # Python deps
├── Dockerfile          # Container image
├── docker-compose.yml  # Docker orchestration
└── README.md           # This file
```

## Database

Default: SQLite (development)

Untuk production, ganti ke PostgreSQL di `.env`:
```env
DATABASE_URL=postgresql://user:pass@db:5432/warehouse
```

## OCR Configuration

OCR menggunakan Tesseract dengan preprocessing:
- Grayscale conversion
- Noise reduction
- Contrast enhancement
- Adaptive threshold

### Supported SN Patterns
- Huawei: `21xxxxxxxxxxxx`
- ZTE: `219xxxxxxxx`
- Standard: `[A-Z0-9]{6,20}`
- With dashes: `XXX-XXXX-XXXX`

## Customization

### Add New Brands
Edit `config.py`:
```python
BRANDS = [
    "YourBrand",
    # ... existing brands
]
```

### Add Categories
Edit `config.py`:
```python
CATEGORIES = {
    "your_category": ["keyword1", "keyword2"],
}
```

## Troubleshooting

### Bot tidak respon
- Check BOT_TOKEN benar
- Check bot tidak di-block user
- Check logs: `docker-compose logs -f bot`

### OCR tidak akurat
- Pastikan foto jelas dan terang
- SN harus readable
- Coba kirim foto dengan resolusi lebih tinggi

### Database locked (SQLite)
- Gunakan PostgreSQL untuk multi-user
- Atau restart container: `docker-compose restart`

## Development

```bash
# Setup dev environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests (if available)
pytest

# Lint
cd warehouse-bot
flake8 .
black .
```

## Production Deployment

1. Gunakan PostgreSQL database
2. Set webhook mode (lebih scalable):
   ```python
   # Di bot.py, ganti polling ke webhook
   await bot.set_webhook(url=WEBHOOK_URL)
   ```
3. Gunakan reverse proxy (nginx/caddy)
4. Setup monitoring dengan health checks

## License

MIT License - Free to use and modify.

## Support

Buat issue atau PR di repository.
