import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from config import KEYWORDS, CATEGORIES

@dataclass
class ParsedItem:
    name: str
    brand: Optional[str] = None
    specs: Optional[str] = None
    quantity: int = 1
    unit: str = "pcs"
    serial_numbers: List[str] = None
    category: str = "unknown"
    
    def __post_init__(self):
        if self.serial_numbers is None:
            self.serial_numbers = []

@dataclass  
class ParsedTransaction:
    type: str  # 'masuk', 'keluar', 'so'
    items: List[ParsedItem]
    purpose: Optional[str] = None
    destination: Optional[str] = None
    source: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

class MessageParser:
    """Parse natural language warehouse messages"""
    
    # Patterns
    QUANTITY_PATTERN = re.compile(
        r'(\d+)\s*(pcs|pasang|unit|gulung|btg|buah|box|set|pair|lembar|meter|m|kg)',
        re.IGNORECASE
    )
    
    SERIAL_PATTERN = re.compile(
        r'(?:SN|sn|S/N|s/n|serial)[\s:]*([A-Z0-9\-]+)',
        re.IGNORECASE
    )
    
    BRAND_PATTERN = re.compile(
        r'(?:merk|brand)\s+([A-Za-z0-9\-]+)',
        re.IGNORECASE
    )
    
    # SFP specs patterns
    SPEED_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*(G|Gbps|Mbps|Mbps?)', re.IGNORECASE)
    DISTANCE_PATTERN = re.compile(r'(\d+)\s*(Km|km|M|m)', re.IGNORECASE)
    WAVELENGTH_PATTERN = re.compile(r'(\d{3,4})\s*(Nm|nm)', re.IGNORECASE)
    
    def detect_transaction_type(self, text: str) -> str:
        """Detect if message is about barang masuk, keluar, or stock opname"""
        text_lower = text.lower()
        
        # Check for rekap/report commands first
        for keyword in KEYWORDS["rekap"]:
            if keyword in text_lower:
                return "rekap"
        
        # Check for SO/Stock Opname
        for keyword in KEYWORDS["so"]:
            if keyword in text_lower:
                return "so"
        
        # Check for barang keluar
        for keyword in KEYWORDS["barang_keluar"]:
            if keyword in text_lower:
                return "keluar"
        
        # Check for barang masuk
        for keyword in KEYWORDS["barang_masuk"]:
            if keyword in text_lower:
                return "masuk"
        
        # Default to keluar if mention "ke" + location
        if re.search(r'\bke\s+(\w+)', text_lower):
            return "keluar"
        
        return "unknown"
    
    def extract_brand(self, text: str) -> Optional[str]:
        """Extract brand/merk from text"""
        # Common brands in warehouse context
        brands = [
            "Huawei", "Cisco", "ZTE", "Mikrotik", "Mikrobits", "TP-Link", "TPLink",
            "Nokia", "Alcatel-Lucent", "Juniper", "HP", "HPE", "Intel", "Finisar",
            "Rapid Network", "Rapid", "Tarmoc", "6Com", "Optone", "WBS", "Gcon",
            "Nufiber", "Yxfiber", "Raisecom", "Ciptara", "Fiberson", "Gigalight",
            "HG Genuine", "Itachi", "WTD", "PBNN", "Etulink", "FS", "No Merk",
            "Inno Light", "AIS", "II-VI", "ZTE"
        ]
        
        text_clean = text.lower()
        for brand in brands:
            if brand.lower() in text_clean:
                return brand
        
        # Try regex pattern
        match = self.BRAND_PATTERN.search(text)
        if match:
            return match.group(1)
        
        return None
    
    def extract_quantity(self, text: str) -> Tuple[int, str]:
        """Extract quantity and unit from text"""
        match = self.QUANTITY_PATTERN.search(text)
        if match:
            qty = int(match.group(1))
            unit = match.group(2).lower()
            # Normalize units
            unit_map = {
                "buah": "pcs",
                "pasang": "pasang",
                "pair": "pasang",
                "btg": "btg",
                "batang": "btg",
                "m": "meter",
                "lembar": "pcs",
                "box": "box",
                "set": "set",
            }
            unit = unit_map.get(unit, unit)
            return qty, unit
        return 1, "pcs"
    
    def extract_serial_numbers(self, text: str) -> List[str]:
        """Extract all serial numbers from text"""
        matches = self.SERIAL_PATTERN.findall(text)
        return [m.strip() for m in matches if len(m.strip()) > 3]
    
    def extract_specs(self, text: str) -> Optional[str]:
        """Extract SFP/optical specs (speed, distance, wavelength)"""
        specs = []
        
        # Speed
        speed_match = self.SPEED_PATTERN.search(text)
        if speed_match:
            speed_val = speed_match.group(1)
            speed_unit = speed_match.group(2).upper()
            if speed_unit in ['G', 'GBPS']:
                specs.append(f"{speed_val}G")
            else:
                specs.append(f"{speed_val}Mbps")
        
        # Distance
        dist_match = self.DISTANCE_PATTERN.search(text)
        if dist_match:
            dist_val = dist_match.group(1)
            dist_unit = dist_match.group(2).lower()
            specs.append(f"{dist_val}{dist_unit}")
        
        # Wavelength
        wave_match = self.WAVELENGTH_PATTERN.search(text)
        if wave_match:
            specs.append(f"{wave_match.group(1)}nm")
        
        return ", ".join(specs) if specs else None
    
    def detect_category(self, text: str) -> str:
        """Detect item category"""
        text_lower = text.lower()
        
        for category, keywords in CATEGORIES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        # SFP specific detection
        if any(x in text_lower for x in ['qsfp', 'sfp', 'bidi', 'gpon', 'olt', 'ont']):
            return "sfp"
        
        return "unknown"
    
    def extract_purpose_destination(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract purpose and destination from text"""
        purpose = None
        destination = None
        source = None
        
        # Destination patterns (barang keluar)
        dest_patterns = [
            r'(?:ke|untuk|tujuan)\s+([^.\n]+)',
            r'(?:branch|cabang|unit|tim)\s+([^.\n]+)',
            r'(?:kebutuhan|project|proyek)\s+([^.\n]+)',
        ]
        
        for pattern in dest_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dest_text = match.group(1).strip()
                # Categorize
                if any(x in dest_text.lower() for x in ['branch', 'cabang']):
                    destination = dest_text
                elif any(x in text.lower() for x in ['kebutuhan', 'project', 'proyek', 'migrasi']):
                    purpose = dest_text
                else:
                    destination = dest_text
                break
        
        # Source patterns (barang masuk)
        source_patterns = [
            r'(?:dari|sumber|sisaan|boq)\s+([^.\n]+)',
        ]
        for pattern in source_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                source = match.group(1).strip()
                break
        
        return purpose, destination or source
    
    def parse_bullet_items(self, text: str) -> List[ParsedItem]:
        """Parse bullet point style items (•, -, *)"""
        items = []
        
        # Split by bullet points
        bullet_pattern = re.compile(r'^[\s]*[•\-\*]\s+(.+)$', re.MULTILINE)
        bullet_matches = bullet_pattern.findall(text)
        
        if bullet_matches:
            for line in bullet_matches:
                item = self.parse_single_item(line)
                if item:
                    items.append(item)
        else:
            # No bullets, treat entire text as one item
            item = self.parse_single_item(text)
            if item:
                items.append(item)
        
        return items
    
    def parse_single_item(self, text: str) -> Optional[ParsedItem]:
        """Parse a single item line"""
        text = text.strip()
        if not text or len(text) < 3:
            return None
        
        # Extract components
        qty, unit = self.extract_quantity(text)
        brand = self.extract_brand(text)
        specs = self.extract_specs(text)
        serials = self.extract_serial_numbers(text)
        category = self.detect_category(text)
        
        # Clean item name (remove specs, qty, brand markers for cleaner name)
        name = text
        
        # Remove quantity part
        qty_match = self.QUANTITY_PATTERN.search(name)
        if qty_match:
            name = name.replace(qty_match.group(0), "").strip()
        
        # Remove SN part
        for sn in serials:
            name = re.sub(rf'(?i)sn[:\s]*{re.escape(sn)}', '', name)
        
        # Remove brackets content for cleaner name
        name = re.sub(r'\[.*?\]', '', name)
        name = re.sub(r'\(.*?\)', '', name)
        
        # Clean up
        name = re.sub(r'\s+', ' ', name).strip()
        name = name.strip('•-*,.:;')
        
        # If name is too short, use original
        if len(name) < 3:
            name = text[:100]  # Limit length
        
        return ParsedItem(
            name=name,
            brand=brand,
            specs=specs,
            quantity=qty,
            unit=unit,
            serial_numbers=serials,
            category=category
        )
    
    def parse_message(self, text: str) -> ParsedTransaction:
        """Main entry point: parse full message"""
        # Detect transaction type
        trans_type = self.detect_transaction_type(text)
        
        if trans_type == "rekap":
            return ParsedTransaction(type="rekap", items=[])
        
        # Extract purpose/destination
        purpose, destination = self.extract_purpose_destination(text)
        
        # Parse items
        items = self.parse_bullet_items(text)
        
        return ParsedTransaction(
            type=trans_type,
            items=items,
            purpose=purpose,
            destination=destination,
            date=datetime.now()
        )

# Helper function for quick parsing
def parse_message(text: str) -> ParsedTransaction:
    parser = MessageParser()
    return parser.parse_message(text)

def format_item_summary(item: ParsedItem) -> str:
    """Format item for confirmation display"""
    parts = []
    if item.brand:
        parts.append(f"📦 {item.brand}")
    parts.append(item.name[:50])
    if item.specs:
        parts.append(f"⚡ {item.specs}")
    parts.append(f"📊 {item.quantity} {item.unit}")
    if item.serial_numbers:
        parts.append(f"🔢 SN: {', '.join(item.serial_numbers[:3])}")
        if len(item.serial_numbers) > 3:
            parts.append(f"   ... dan {len(item.serial_numbers)-3} SN lainnya")
    
    return "\n".join(parts)
