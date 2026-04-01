import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
TEMP_DIR = BASE_DIR / "temp"

# Create directories
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Bot config
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Google Sheets config
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1ZdXAGxDnXZBDGnriXA7jJX9QVA9ANnbbSuAXzf5LbHo/edit?gid=0#gid=0")

# Parse ADMIN_IDS with error handling
_admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = []
if _admin_ids_raw:
    for x in _admin_ids_raw.split(","):
        x = x.strip()
        if x:
            try:
                ADMIN_IDS.append(int(x))
            except ValueError:
                print(f"⚠️ Warning: ADMIN_IDS contains invalid value '{x}' - must be a number (Telegram User ID)")
                print(f"   Get your User ID from @userinfobot")
                # Skip invalid values instead of crashing

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/warehouse.db")

# OCR
_default_tesseract = "tesseract"
if os.name == "nt":
    for _path in [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")
    ]:
        if os.path.exists(_path):
            _default_tesseract = _path
            break

TESSERACT_CMD = os.getenv("TESSERACT_CMD", _default_tesseract)

# Report settings
TIMEZONE = os.getenv("REPORT_TIMEZONE", "Asia/Jakarta")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Warehouse System")

# Keywords untuk parsing
KEYWORDS = {
    "barang_masuk": ["masuk", "terima", "sisaan", "stock masuk", "barang masuk", "diterima"],
    "barang_keluar": ["keluar", "ambil", "pakai", "digunakan", "kirim", "dikirim", "kebutuhan", "barang keluar"],
    "so": ["so", "stock opname", "opname"],
    "rekap": ["rekap", "report", "laporan", "ringkasan", "list"],
}

# Item categories
CATEGORIES = {
    "sfp": ["sfp", "gpon", "olt", "modul"],
    "battery": ["baterai", "battery", "aki", "accu", "pjuts"],
    "cable": ["kabel", "cabel", "fiber", "fo"],
    "router": ["router", "ont", "modem", "switch"],
    "misc": ["tiang", "solasi", "isolasi", "alat"],
}

# Warehouse Staff List (simple ID: Name format for easy use)
WAREHOUSE_STAFF = {
    1: "Agus",
    2: "Rohman",
    3: "Dewa",
    4: "Irfan"
}
