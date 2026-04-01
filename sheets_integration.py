import gspread_asyncio
from google.oauth2.service_account import Credentials
import logging
from datetime import datetime
from config import BASE_DIR, GOOGLE_SHEET_URL

logger = logging.getLogger(__name__)
CREDENTIALS_FILE = BASE_DIR / "credentials.json"

def get_creds():
    creds = Credentials.from_service_account_file(str(CREDENTIALS_FILE))
    scoped = creds.with_scopes([
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped

agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)

async def append_transactions_to_sheet(parsed, staff_name, trans_type_str):
    try:
        if not CREDENTIALS_FILE.exists():
            logger.warning("credentials.json not found. Skipping Google Sheets sync.")
            return

        agc = await agcm.authorize()
        ss = await agc.open_by_url(GOOGLE_SHEET_URL)
        
        # Buka sheet pertama
        sheet = await ss.get_worksheet(0)
        
        # Siapkan header jika kosong
        sheet_records = await sheet.get_all_values()
        if not sheet_records:
            header = ["Waktu", "Staff", "Tipe", "Kategori", "Barang", "Merk", "Spesifikasi", "Quantity", "SN", "Tujuan/Sumber", "Keperluan"]
            await sheet.append_row(header)
            
        rows_to_append = []
        for item in parsed.items:
            rows_to_append.append([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                staff_name,
                trans_type_str.upper(),
                item.category.upper() if item.category else "-",
                item.name,
                item.brand or "-",
                item.specs or "-",
                f"{item.quantity} {item.unit}",
                ", ".join(item.serial_numbers) if item.serial_numbers else "-",
                parsed.destination or parsed.source or "-",
                parsed.purpose or "-"
            ])
            
        await sheet.append_rows(rows_to_append)
        logger.info(f"Successfully synced {len(rows_to_append)} rows to Google Sheets.")
    except Exception as e:
        logger.error(f"Failed to append to Google Sheets: {e}")
