from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, 
    Text, Float, ForeignKey, Enum, Boolean, func
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import enum

from config import DATABASE_URL

Base = declarative_base()

class TransactionType(enum.Enum):
    MASUK = "masuk"      # Barang masuk
    KELUAR = "keluar"    # Barang keluar
    SO = "so"            # Stock Opname

class ItemCategory(enum.Enum):
    SFP = "sfp"
    BATTERY = "battery"
    CABLE = "cable"
    ROUTER = "router"
    MISC = "misc"
    UNKNOWN = "unknown"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    full_name = Column(String(200))
    role = Column(String(50), default="user")  # admin, user, warehouse_staff
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Staff info (who recorded this transaction)
    staff_id = Column(Integer)                      # ID from WAREHOUSE_STAFF (1-4)
    staff_name = Column(String(100))               # Name: Agus, Rohman, Dewa, Irfan
    
    type = Column(Enum(TransactionType), nullable=False)
    category = Column(Enum(ItemCategory), default=ItemCategory.UNKNOWN)
    
    # Item details
    item_name = Column(String(500), nullable=False)  # Nama lengkap barang
    brand = Column(String(100))                     # Merk
    specs = Column(Text)                            # Spesifikasi (speed, distance, wavelength)
    quantity = Column(Integer, default=1)           # Jumlah
    unit = Column(String(20), default="pcs")        # Unit: pcs, pasang, unit, gulung, btg
    
    # Serial Numbers (JSON string untuk multiple SN)
    serial_numbers = Column(Text)  # JSON list ["SN001", "SN002"]
    has_serial = Column(Boolean, default=False)
    
    # Additional info
    purpose = Column(Text)          # Tujuan/keperluan
    destination = Column(Text)      # Tujuan pengiriman/cabang
    source = Column(Text)             # Sumber barang masuk
    notes = Column(Text)            # Catatan tambahan
    
    # Photos
    photo_paths = Column(Text)      # JSON list paths foto
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    transaction_date = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="transactions")

class DailyReport(Base):
    __tablename__ = "daily_reports"
    
    id = Column(Integer, primary_key=True)
    report_date = Column(DateTime, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id"))
    generated_at = Column(DateTime, default=datetime.now)
    
    # Summary counts
    total_masuk = Column(Integer, default=0)
    total_keluar = Column(Integer, default=0)
    total_so = Column(Integer, default=0)
    
    # Report content
    content_text = Column(Text)     # Full text report
    excel_path = Column(String(500))  # Path ke file Excel
    
    is_finalized = Column(Boolean, default=False)

# Database setup
def get_engine():
    """Get sync engine (for migrations)"""
    db_url = DATABASE_URL
    if db_url.startswith("sqlite"):
        return create_engine(db_url, echo=False)
    return create_engine(db_url)

def init_db():
    """Initialize database tables"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get sync session (for background tasks)"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# Async versions for bot
async def get_async_engine():
    db_url = DATABASE_URL
    if db_url.startswith("sqlite"):
        # SQLite async support
        db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        return create_async_engine(db_url, echo=False)
    elif db_url.startswith("postgresql"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        return create_async_engine(db_url)
    return create_async_engine(db_url)

async def get_async_session():
    engine = await get_async_engine()
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session()
