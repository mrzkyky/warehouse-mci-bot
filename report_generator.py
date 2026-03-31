from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import pandas as pd
from io import BytesIO
import os

from models import Transaction, TransactionType, User, ItemCategory
from config import REPORTS_DIR, COMPANY_NAME
from parser import ParsedItem

class ReportGenerator:
    """Generate daily warehouse reports"""
    
    def __init__(self, session: Session):
        self.session = session
        self.report_date = datetime.now()
    
    def get_transactions_for_date(
        self, 
        date: datetime, 
        trans_type: Optional[TransactionType] = None
    ) -> List[Transaction]:
        """Get transactions for specific date"""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        query = self.session.query(Transaction).filter(
            and_(
                Transaction.transaction_date >= start_of_day,
                Transaction.transaction_date < end_of_day
            )
        )
        
        if trans_type:
            query = query.filter(Transaction.type == trans_type)
        
        return query.order_by(Transaction.created_at).all()
    
    def get_today_transactions(self, trans_type: Optional[TransactionType] = None) -> List[Transaction]:
        """Get today's transactions"""
        return self.get_transactions_for_date(datetime.now(), trans_type)
    
    def format_item_line(self, item: Transaction, index: int) -> str:
        """Format single item for text report"""
        lines = []
        
        # Item name with brand
        name_parts = []
        if item.brand:
            name_parts.append(f"•{item.brand}")
        name_parts.append(item.item_name)
        
        line = f"{index}. {' '.join(name_parts)}"
        
        # Add specs if available
        if item.specs:
            line += f" ({item.specs})"
        
        # Quantity
        line += f" = {item.quantity} {item.unit}"
        lines.append(line)
        
        # Staff info (NEW)
        if item.staff_name:
            lines.append(f"   👤 Oleh: {item.staff_name}")
        
        # Serial numbers
        if item.serial_numbers:
            try:
                sns = eval(item.serial_numbers) if item.serial_numbers.startswith('[') else [item.serial_numbers]
                for sn in sns:
                    lines.append(f"   🔢 SN: {sn}")
            except:
                if item.serial_numbers:
                    lines.append(f"   🔢 SN: {item.serial_numbers}")
        
        # Notes
        if item.notes:
            lines.append(f"   📝 {item.notes}")
        
        return "\n".join(lines)
    
    def generate_text_report(self, date: Optional[datetime] = None) -> str:
        """Generate text report similar to user's example"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%d %B %Y")
        
        lines = []
        lines.append(f"📦 *DAILY REPORT GUDANG*")
        lines.append(f"📅 {date_str}")
        lines.append(f"🏢 {COMPANY_NAME}")
        lines.append("=" * 40)
        
        # Barang Keluar
        keluar_items = self.get_transactions_for_date(date, TransactionType.KELUAR)
        if keluar_items:
            lines.append("")
            lines.append(f"📤 *BARANG KELUAR* ({len(keluar_items)} item)")
            lines.append("-" * 30)
            
            # Group by purpose/destination
            by_destination = {}
            for item in keluar_items:
                dest = item.destination or item.purpose or "Umum"
                if dest not in by_destination:
                    by_destination[dest] = []
                by_destination[dest].append(item)
            
            for dest, items in by_destination.items():
                lines.append(f"\n🏷️ {dest}")
                for i, item in enumerate(items, 1):
                    lines.append(self.format_item_line(item, i))
        
        # Barang Masuk
        masuk_items = self.get_transactions_for_date(date, TransactionType.MASUK)
        if masuk_items:
            lines.append("")
            lines.append(f"📥 *BARANG MASUK* ({len(masuk_items)} item)")
            lines.append("-" * 30)
            
            # Group by source
            by_source = {}
            for item in masuk_items:
                src = item.source or "Umum"
                if src not in by_source:
                    by_source[src] = []
                by_source[src].append(item)
            
            for src, items in by_source.items():
                lines.append(f"\n📍 {src}")
                for i, item in enumerate(items, 1):
                    lines.append(self.format_item_line(item, i))
        
        # Stock Opname
        so_items = self.get_transactions_for_date(date, TransactionType.SO)
        if so_items:
            lines.append("")
            lines.append(f"📊 *STOCK OPNAME* ({len(so_items)} item)")
            lines.append("-" * 30)
            
            # Group by category
            by_category = {}
            for item in so_items:
                cat = item.category.value if item.category else "Lainnya"
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(item)
            
            for cat, items in by_category.items():
                lines.append(f"\n📁 {cat.upper()}")
                for i, item in enumerate(items, 1):
                    lines.append(self.format_item_line(item, i))
        
        # Summary
        total_keluar = len(keluar_items)
        total_masuk = len(masuk_items)
        total_so = len(so_items)
        
        lines.append("")
        lines.append("=" * 40)
        lines.append(f"📈 *RINGKASAN:*")
        lines.append(f"   📤 Keluar: {total_keluar} item")
        lines.append(f"   📥 Masuk: {total_masuk} item")
        lines.append(f"   📊 Opname: {total_so} item")
        lines.append(f"   📦 Total: {total_keluar + total_masuk + total_so} item")
        
        return "\n".join(lines)
    
    def generate_excel_report(self, date: Optional[datetime] = None) -> str:
        """Generate Excel report and return file path"""
        
        # Get all transactions
        transactions = self.session.query(Transaction).order_by(Transaction.created_at).all()
        
        # Create Excel writer
        file_path = REPORTS_DIR / "laporan_gudang_master.xlsx"
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            if not transactions:
                # Empty report
                pd.DataFrame({"Info": ["Belum ada transaksi"]}).to_excel(writer, sheet_name='Kosong', index=False)
                return str(file_path)
            
            # Group by date
            from collections import defaultdict
            by_date = defaultdict(list)
            for t in transactions:
                date_str = t.transaction_date.strftime("%d-%b-%Y")
                by_date[date_str].append(t)
            
            # Convert to DataFrame
            def transactions_to_df(trans_list):
                data = []
                for t in trans_list:
                    sns = []
                    if t.serial_numbers:
                        try:
                            sns = eval(t.serial_numbers) if t.serial_numbers.startswith('[') else [t.serial_numbers]
                        except:
                            sns = [t.serial_numbers]
                    
                    data.append({
                        'Tipe': t.type.value.upper() if t.type else '-',
                        'Waktu': t.created_at.strftime("%H:%M"),
                        'Staff': t.staff_name or '-',
                        'Nama Barang': t.item_name,
                        'Merk': t.brand or '-',
                        'Spesifikasi': t.specs or '-',
                        'Jumlah': t.quantity,
                        'Unit': t.unit,
                        'Serial Numbers': ', '.join(sns) if sns else '-',
                        'Tujuan/Sumber': t.destination or t.source or '-',
                        'Keperluan': t.purpose or '-',
                        'Kategori': t.category.value.upper() if t.category else '-',
                        'Catatan': t.notes or '-'
                    })
                return pd.DataFrame(data)
            
            for date_str, trans_list in by_date.items():
                df = transactions_to_df(trans_list)
                df = df.sort_values(by=['Tipe', 'Waktu'])
                df.to_excel(writer, sheet_name=date_str[:31], index=False)
        
        return str(file_path)
    
    def generate_so_report(self, date: Optional[datetime] = None) -> str:
        """Generate Stock Opname report in the user's format"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%d %B %Y")
        
        lines = []
        lines.append(f"{{SO {date_str}}}")
        lines.append("")
        
        so_items = self.get_transactions_for_date(date, TransactionType.SO)
        
        # Group by category
        by_category = {}
        for item in so_items:
            cat = item.category.value if item.category else "Lainnya"
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)
        
        for cat, items in by_category.items():
            lines.append(f"∆Data {cat.upper()}")
            
            # Group by subcategory if available
            for item in items:
                name = item.item_name
                if item.brand:
                    name = f"•{item.brand} {name}"
                else:
                    name = f"•{name}"
                
                specs = []
                if item.specs:
                    specs.append(item.specs)
                
                line = f"{name} ({item.quantity}{item.unit})"
                if specs:
                    line += f" [{'/'.join(specs)}]"
                
                lines.append(line)
            
            lines.append("")
        
        return "\n".join(lines)

def generate_daily_report(session: Session, date: Optional[datetime] = None, format: str = "text"):
    """Convenience function to generate report"""
    generator = ReportGenerator(session)
    
    if format == "text":
        return generator.generate_text_report(date)
    elif format == "excel":
        return generator.generate_excel_report(date)
    elif format == "so":
        return generator.generate_so_report(date)
    else:
        return generator.generate_text_report(date)
