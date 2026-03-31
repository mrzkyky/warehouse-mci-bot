import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_IDS, TEMP_DIR, COMPANY_NAME, WAREHOUSE_STAFF
from models import (
    init_db, get_session, Transaction, TransactionType, 
    ItemCategory, User
)
from parser import MessageParser, format_item_summary, parse_message
from ocr import SerialNumberOCR, format_ocr_result
from report_generator import generate_daily_report

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot setup
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# State management
class Form(StatesGroup):
    waiting_for_confirmation = State()
    waiting_for_photo = State()
    waiting_for_sn_confirmation = State()
    selecting_staff = State()  # New: user selecting warehouse staff name

# Helper functions
async def clear_state_keep_staff(state: FSMContext):
    """Clear state but preserve staff_id and staff_name."""
    data = await state.get_data()
    staff_id = data.get('staff_id')
    staff_name = data.get('staff_name')
    await state.clear()
    if staff_id and staff_name:
        await state.update_data(staff_id=staff_id, staff_name=staff_name)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def get_or_create_user(session, telegram_user) -> User:
    """Get existing user or create new one"""
    user = session.query(User).filter_by(telegram_id=telegram_user.id).first()
    if not user:
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            full_name=telegram_user.full_name,
            role="user"
        )
        session.add(user)
        session.commit()
    return user

def create_confirmation_keyboard():
    """Create yes/no keyboard for confirmation"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Benar", callback_data="confirm_yes")
    builder.button(text="❌ Salah", callback_data="confirm_no")
    builder.button(text="📝 Edit", callback_data="confirm_edit")
    builder.adjust(2, 1)
    return builder.as_markup()

def create_main_menu_keyboard():
    """Create main menu keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📤 Barang Keluar", callback_data="menu_keluar")
    builder.button(text="📥 Barang Masuk", callback_data="menu_masuk")
    builder.button(text="📊 Stock Opname", callback_data="menu_so")
    builder.button(text="📸 Scan SN", callback_data="menu_scan")
    builder.button(text="📋 Rekap Hari Ini", callback_data="menu_rekap")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def create_staff_selection_keyboard():
    """Create keyboard for staff selection"""
    builder = InlineKeyboardBuilder()
    for staff_id, staff_name in WAREHOUSE_STAFF.items():
        builder.button(text=f"👤 {staff_name}", callback_data=f"staff_{staff_id}")
    builder.adjust(2)  # 2 buttons per row
    return builder.as_markup()

async def ask_staff_selection(message: Message, state: FSMContext):
    """Ask user to select warehouse staff"""
    await state.set_state(Form.selecting_staff)
    await message.answer(
        "👋 *Selamat Datang!*\n\n"
        "Siapa nama Anda? Pilih dari list:",
        parse_mode="Markdown",
        reply_markup=create_staff_selection_keyboard()
    )

# Command handlers
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start command handler"""
    # Check if user has selected staff
    data = await state.get_data()
    staff_name = data.get('staff_name')
    
    if not staff_name:
        # First time - ask to select staff
        await ask_staff_selection(message, state)
        return
    
    # Already selected, show welcome
    welcome_text = f"""
👋 *Selamat datang di {COMPANY_NAME} Warehouse Bot!*

Bot ini membantu mencatat barang masuk, keluar, dan stock opname via Telegram.

*Cara penggunaan:*
1️⃣ *Chat langsung* - Kirim pesan deskripsi barang
2️⃣ *Foto + SN* - Kirim foto label barang untuk scan SN
3️⃣ *Rekap* - Ketik "rekap" untuk laporan harian

*Contoh pesan:*
📤 *Barang Keluar:*
`Kebutuhan migrasi server unit JTB`
`- DCDU 12B huawei (1 unit)`
`SN: 21021207316TL4922814`

📥 *Barang Masuk:*
`sisaan BOQ jatibarang > rajak`
`- tiang 3inch 7m Biasa (25 Btg)`

📊 *Stock Opname:*
`SO 15 Maret 2026`
`Data Sfp`
`•Huawei 155Mbps 15Km 1310Nm (2pcs)`

Ketik /help untuk bantuan lebih lanjut.
    """
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=create_main_menu_keyboard())

# Staff selection callback handler
@dp.callback_query(Form.selecting_staff, F.data.startswith("staff_"))
async def process_staff_selection(callback: CallbackQuery, state: FSMContext):
    """Handle staff selection"""
    staff_id = int(callback.data.split("_")[1])
    staff_name = WAREHOUSE_STAFF.get(staff_id, "Unknown")
    
    # Save to state
    await state.update_data(staff_id=staff_id, staff_name=staff_name)
    await clear_state_keep_staff(state)  # Clear selection state
    
    await callback.answer(f"Halo {staff_name}!")
    await callback.message.edit_text(
        f"✅ *Halo {staff_name}!*\n\n"
        f"Anda sudah terdaftar sebagai staff gudang.\n"
        f"Silakan mulai mencatat barang.",
        parse_mode="Markdown",
        reply_markup=create_main_menu_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Help command handler"""
    help_text = """
📚 *Panduan Penggunaan*

*Format Pesan:*

1️⃣ *Barang Keluar:*
```
Kebutuhan [tujuan]
- [nama barang] ([qty] [unit])
SN: [serial number]
```

2️⃣ *Barang Masuk:*
```
[dari/sumber]
- [nama barang] ([qty] [unit])
SN: [serial number]
```

3️⃣ *Stock Opname:*
```
SO [tanggal]
[kategori]
•[merk] [nama] [spesifikasi] ([qty] [unit])
```

*Unit yang didukung:* pcs, pasang, unit, gulung, btg, meter, box, set

*Perintah:*
/rekap - Laporan harian
/scan - Scan SN dari foto
/batal - Batalkan input saat ini
/staff - Ganti staff yang aktif
/help - Tampilkan bantuan ini
    """
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("staff"))
async def cmd_change_staff(message: Message, state: FSMContext):
    """Change current staff"""
    # Clear current staff and ask to select again
    await state.update_data(staff_id=None, staff_name=None)
    await ask_staff_selection(message, state)

@dp.message(Command("rekap"))
async def cmd_rekap(message: Message):
    """Generate daily report"""
    await message.answer("⏳ Sedang membuat laporan...")
    
    try:
        session = get_session()
        
        # Generate text report
        report_text = generate_daily_report(session, format="text")
        
        # Send text report
        await message.answer(report_text, parse_mode="Markdown")
        
        # Generate and send Excel
        excel_path = generate_daily_report(session, format="excel")
        if Path(excel_path).exists():
            await message.answer_document(
                FSInputFile(excel_path),
                caption="📊 Laporan Excel lengkap"
            )
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        await message.answer(f"❌ Error membuat laporan: {str(e)}")
    finally:
        session.close()

@dp.message(Command("scan"))
async def cmd_scan(message: Message, state: FSMContext):
    """Initiate SN scan from photo"""
    await state.set_state(Form.waiting_for_photo)
    await message.answer(
        "📸 *Scan Serial Number*\n\n"
        "Silakan kirim foto label barang yang jelas.\n"
        "Pastikan SN terbaca dengan baik.",
        parse_mode="Markdown"
    )

@dp.message(Command("batal"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current operation"""
    current_state = await state.get_state()
    if current_state:
        await clear_state_keep_staff(state)
        await message.answer("✅ Operasi dibatalkan.", reply_markup=create_main_menu_keyboard())
    else:
        await message.answer("Tidak ada operasi yang berjalan.")

# Callback handlers
@dp.callback_query(F.data == "menu_keluar")
async def on_menu_keluar(callback: CallbackQuery):
    await callback.message.edit_text(
        "📤 *Barang Keluar*\n\n"
        "Kirim pesan dengan format:\n"
        "```\n"
        "Kebutuhan [tujuan/project]\n"
        "- [nama barang] ([jumlah] [unit])\n"
        "SN: [serial number jika ada]\n"
        "```",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_masuk")
async def on_menu_masuk(callback: CallbackQuery):
    await callback.message.edit_text(
        "📥 *Barang Masuk*\n\n"
        "Kirim pesan dengan format:\n"
        "```\n"
        "[Sumber barang: sisaan/dari/penerimaan]\n"
        "- [nama barang] ([jumlah] [unit])\n"
        "SN: [serial number jika ada]\n"
        "```",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_so")
async def on_menu_so(callback: CallbackQuery):
    await callback.message.edit_text(
        "📊 *Stock Opname*\n\n"
        "Kirim pesan dengan format:\n"
        "```\n"
        "SO [tanggal]\n"
        "Data [kategori]\n"
        "•[merk] [nama] [spec] ([jumlah] [unit])\n"
        "```",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_scan")
async def on_menu_scan(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_photo)
    await callback.message.edit_text(
        "📸 *Scan Serial Number*\n\n"
        "Silakan kirim foto label barang yang jelas.",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_rekap")
async def on_menu_rekap(callback: CallbackQuery):
    await cmd_rekap(callback.message)
    await callback.answer()

# Photo handler for OCR
@dp.message(F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Process photo for OCR"""
    await message.answer("🔍 Sedang scan foto...")
    
    try:
        # Download photo
        photo = message.photo[-1]  # Highest resolution
        file = await bot.get_file(photo.file_id)
        
        # Save temporarily
        temp_path = TEMP_DIR / f"scan_{message.from_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        await bot.download_file(file.file_path, destination=temp_path)
        
        # OCR
        ocr = SerialNumberOCR()
        result = ocr.process_image(str(temp_path))
        
        # Format result
        response = format_ocr_result(result)
        
        # Store in state for potential transaction
        await state.update_data(
            photo_path=str(temp_path),
            detected_serials=result.serial_numbers,
            detected_brand=result.brand
        )
        
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="✅ Simpan ke transaksi", callback_data="save_sn")
        keyboard.button(text="🔄 Scan ulang", callback_data="menu_scan")
        keyboard.button(text="❌ Batal", callback_data="cancel_scan")
        
        await message.answer(
            f"📸 *Hasil Scan:*\n\n{response}",
            parse_mode="Markdown",
            reply_markup=keyboard.as_markup()
        )
        
        await state.set_state(Form.waiting_for_sn_confirmation)
        
    except Exception as e:
        logger.error(f"OCR error: {e}")
        await message.answer(f"❌ Error scan foto: {str(e)}")
        await clear_state_keep_staff(state)

@dp.callback_query(Form.waiting_for_sn_confirmation, F.data == "save_sn")
async def on_save_sn(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply(
        "✅ SN siap digunakan!\n\n"
        "Silakan *copy* SN di atas lalu lakukan pencatatan Barang Keluar/Masuk seperti biasa.\n"
        "(Sertakan `SN: [hasil paste]` di pesan transaksi Anda)",
        parse_mode="Markdown"
    )
    await state.set_state(None)

@dp.callback_query(Form.waiting_for_sn_confirmation, F.data == "cancel_scan")
async def on_cancel_scan(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "❌ Scan dibatalkan.",
        reply_markup=create_main_menu_keyboard()
    )
    await clear_state_keep_staff(state)

# Text message handler
@dp.message(F.text)
async def process_text_message(message: Message, state: FSMContext):
    """Process text messages (transactions)"""
    text = message.text
    user = message.from_user
    
    # Parse message
    parser = MessageParser()
    parsed = parser.parse_message(text)
    
    # Check for rekap command in text
    if parsed.type == "rekap":
        await cmd_rekap(message)
        return
    
    if not parsed.items:
        await message.answer(
            "❓ Pesan tidak terdeteksi sebagai transaksi.\n\n"
            "Gunakan /help untuk melihat format yang benar.",
            reply_markup=create_main_menu_keyboard()
        )
        return
    
    # Format for confirmation
    lines = []
    lines.append(f"📋 *Konfirmasi Transaksi* ({parsed.type.upper()})")
    if parsed.purpose:
        lines.append(f"🎯 Keperluan: {parsed.purpose}")
    if parsed.destination:
        lines.append(f"📍 Tujuan: {parsed.destination}")
    lines.append("")
    lines.append("*Items:*")
    
    for i, item in enumerate(parsed.items, 1):
        lines.append(f"\n{i}. {item.name}")
        if item.brand:
            lines.append(f"   🏷️ Merk: {item.brand}")
        lines.append(f"   📊 {item.quantity} {item.unit}")
        if item.serial_numbers:
            lines.append(f"   🔢 SN: {', '.join(item.serial_numbers)}")
    
    # Store parsed data in state
    await state.update_data(
        parsed_data=parsed,
        raw_text=text
    )
    
    await state.set_state(Form.waiting_for_confirmation)
    
    await message.answer(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=create_confirmation_keyboard()
    )

# Confirmation callbacks
@dp.callback_query(Form.waiting_for_confirmation, F.data == "confirm_yes")
async def confirm_transaction(callback: CallbackQuery, state: FSMContext):
    """Save confirmed transaction"""
    data = await state.get_data()
    parsed = data.get('parsed_data')
    raw_text = data.get('raw_text')
    staff_id = data.get('staff_id')
    staff_name = data.get('staff_name')
    
    if not parsed:
        await callback.answer("Data tidak ditemukan!")
        return
    
    # If no staff selected, ask to select first
    if not staff_id:
        await callback.message.edit_text(
            "⚠️ *Silakan pilih nama staff dulu!*\nKetik /start untuk memilih.",
            parse_mode="Markdown"
        )
        await clear_state_keep_staff(state)
        return
    
    try:
        session = get_session()
        user_db = await get_or_create_user(session, callback.from_user)
        
        # Map type
        type_map = {
            "masuk": TransactionType.MASUK,
            "keluar": TransactionType.KELUAR,
            "so": TransactionType.SO
        }
        trans_type = type_map.get(parsed.type, TransactionType.KELUAR)
        
        # Save each item
        saved_count = 0
        for item in parsed.items:
            transaction = Transaction(
                user_id=user_db.id,
                staff_id=staff_id,
                staff_name=staff_name,
                type=trans_type,
                category=ItemCategory(item.category) if item.category in [c.value for c in ItemCategory] else ItemCategory.UNKNOWN,
                item_name=item.name,
                brand=item.brand,
                specs=item.specs,
                quantity=item.quantity,
                unit=item.unit,
                serial_numbers=json.dumps(item.serial_numbers) if item.serial_numbers else None,
                has_serial=bool(item.serial_numbers),
                purpose=parsed.purpose,
                destination=parsed.destination if trans_type == TransactionType.KELUAR else None,
                source=parsed.destination if trans_type == TransactionType.MASUK else None,
                notes=None
            )
            session.add(transaction)
            saved_count += 1
        
        session.commit()
        
        await callback.message.edit_text(
            f"✅ *Transaksi tersimpan!*\n\n"
            f"👤 Staff: {staff_name}\n"
            f"📦 {saved_count} item tercatat\n"
            f"📁 Tipe: {parsed.type.upper()}\n\n"
            f"Ketik /rekap untuk laporan hari ini.",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error saving transaction: {e}")
        await callback.message.edit_text(f"❌ Error menyimpan: {str(e)}")
    finally:
        session.close()
        await clear_state_keep_staff(state)

@dp.callback_query(Form.waiting_for_confirmation, F.data == "confirm_no")
async def reject_transaction(callback: CallbackQuery, state: FSMContext):
    """Reject transaction"""
    await clear_state_keep_staff(state)
    await callback.message.edit_text(
        "❌ Transaksi dibatalkan.\n\n"
        "Kirim pesan baru dengan format yang benar.",
        reply_markup=create_main_menu_keyboard()
    )
    await callback.answer("Dibatalkan")

@dp.callback_query(Form.waiting_for_confirmation, F.data == "confirm_edit")
async def edit_transaction(callback: CallbackQuery, state: FSMContext):
    """Request edit"""
    await clear_state_keep_staff(state)
    await callback.message.edit_text(
        "✏️ Silakan kirim ulang pesan dengan perbaikan.",
        reply_markup=create_main_menu_keyboard()
    )
    await callback.answer()

# Error handler
@dp.errors()
async def error_handler(exception):
    logger.error(f"Update error: {exception}")

# Main entry point
async def main():
    """Start the bot"""
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
