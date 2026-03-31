# Project Structure

```
warehouse-bot/
├── 📁 Core Application
│   ├── bot.py              # Main Telegram bot handler
│   ├── parser.py           # NLP message parser
│   ├── ocr.py              # Serial Number OCR
│   ├── report_generator.py # Report generation (text/Excel)
│   └── models.py           # Database models (SQLAlchemy)
│
├── 📁 Configuration
│   ├── config.py           # App configuration & constants
│   ├── .env                # Environment variables (gitignored)
│   └── .env.example        # Example environment file
│
├── 📁 Deployment
│   ├── Dockerfile          # Docker image definition
│   ├── docker-compose.yml  # Docker orchestration
│   ├── setup.py            # Setup script
│   └── Makefile            # Convenience commands
│
├── 📁 Documentation
│   ├── README.md           # Main documentation
│   ├── INSTALL.md          # Installation guide
│   ├── WORKFLOW.md         # User workflow guide
│   └── PROJECT_STRUCTURE.md # This file
│
├── 📁 Testing & Admin
│   ├── test_parser.py      # Parser unit tests
│   └── admin.py            # Admin CLI tools
│
├── 📁 Data (gitignored)
│   ├── data/               # SQLite database
│   ├── reports/            # Generated reports
│   └── temp/               # Temporary files (photos)
│
├── 📁 Project Meta
│   ├── requirements.txt    # Python dependencies
│   ├── .gitignore          # Git ignore rules
│   └── .dockerignore       # Docker ignore rules
│
└── 📁 Runtime (created on first run)
    ├── data/warehouse.db   # SQLite database file
    ├── reports/*.xlsx      # Generated Excel reports
    └── temp/*.jpg          # Temporary OCR images
```

## File Responsibilities

### Core Files

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `bot.py` | Telegram bot interface | `main()`, command handlers |
| `parser.py` | Natural language parsing | `MessageParser`, `parse_message()` |
| `ocr.py` | Image processing & OCR | `SerialNumberOCR`, `quick_scan()` |
| `report_generator.py` | Report generation | `ReportGenerator`, `generate_daily_report()` |
| `models.py` | Database schema | `Transaction`, `User`, `TransactionType` |
| `config.py` | App settings | `KEYWORDS`, `CATEGORIES`, constants |

### Data Flow

```
User Input (Text/Foto)
    ↓
[bot.py] Telegram Handler
    ↓
[parser.py] NLP Parsing  OR  [ocr.py] Image OCR
    ↓
[models.py] Database Storage
    ↓
[report_generator.py] Report Generation
    ↓
User Output (Text/Excel)
```

## Architecture Overview

### 1. Bot Layer (`bot.py`)
- Handles Telegram API communication
- Manages user sessions (FSM)
- Routes commands to appropriate handlers
- Formats responses

### 2. Parser Layer (`parser.py`)
- Pattern matching untuk deteksi:
  - Transaction type (masuk/keluar/so)
  - Quantity & unit
  - Brand detection
  - Specs extraction (speed/distance/wavelength)
  - Serial number extraction
- Returns structured `ParsedTransaction`

### 3. OCR Layer (`ocr.py`)
- Preprocessing: grayscale, denoise, contrast
- Tesseract OCR
- Postprocessing: SN pattern matching
- Returns `OCRResult` dengan SN list

### 4. Data Layer (`models.py`)
- SQLAlchemy ORM
- Tables: users, transactions, daily_reports
- Supports SQLite (dev) & PostgreSQL (prod)

### 5. Report Layer (`report_generator.py`)
- Aggregates transactions by date
- Generates:
  - WhatsApp-friendly text
  - Excel with multiple sheets
  - Stock Opname format

### 6. Config Layer (`config.py`)
- Environment variables
- Keywords untuk NLP
- Brand & category lists
- File paths

## Extension Points

### Add New Brand
Edit `config.py`:
```python
BRANDS.append("YourBrand")
```

### Add New Category
Edit `config.py`:
```python
CATEGORIES["new_cat"] = ["keyword1", "keyword2"]
```

### Custom Report Format
Edit `report_generator.py`:
- Add new method di `ReportGenerator`
- Register di `generate_daily_report()`

### New Command
Edit `bot.py`:
- Add handler with `@dp.message(Command("newcmd"))`
- Implement logic

## Dependencies Graph

```
config.py
    ↓ (used by all)
models.py
    ↓ (used by)
    ├── bot.py
    ├── report_generator.py
    └── admin.py

parser.py
    ↓ (used by)
    └── bot.py

ocr.py
    ↓ (used by)
    └── bot.py

report_generator.py
    ↓ (used by)
    ├── bot.py
    └── admin.py
```

## Design Patterns

1. **Repository Pattern**: `models.py` abstracts database
2. **Strategy Pattern**: `parser.py` pluggable parsers
3. **Factory Pattern**: `config.py` creates paths/settings
4. **Template Method**: `report_generator.py` base report class

## Performance Considerations

- **OCR**: CPU intensive, run asynchronously
- **Database**: SQLite = single writer, use PostgreSQL for scale
- **Photos**: Auto-deleted after processing (configurable)
- **Reports**: Generated on-demand, cached via file system

## Security

- Bot token di `.env` (gitignored)
- Admin check via `ADMIN_IDS`
- SQL injection protected (SQLAlchemy ORM)
- File upload validation (photo only)
- No sensitive data di logs

## Testing

```bash
# Unit tests
python test_parser.py

# Integration
python admin.py stats
python admin.py report

# Manual testing via Telegram
```

## Deployment Modes

| Mode | Use Case | Database | Scalability |
|------|----------|----------|-------------|
| Dev | Local testing | SQLite | Single user |
| Docker | Small team | SQLite/Postgres | 10s of users |
| Webhook | Production | Postgres | 100s of users |
| Serverless | Enterprise | Postgres | 1000s of users |
