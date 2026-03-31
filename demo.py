#!/usr/bin/env python3
"""
Demo script - Test parser tanpa dependencies
"""

import sys
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

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
    type: str
    items: List[ParsedItem]
    purpose: Optional[str] = None
    destination: Optional[str] = None

class MessageParser:
    QUANTITY_PATTERN = re.compile(r'(\d+)\s*(pcs|pasang|unit|gulung|btg|buah|box|set|pair|lembar|meter|m|kg)', re.IGNORECASE)
    SERIAL_PATTERN = re.compile(r'(?:SN|sn|S/N|s/n|serial)[\s:]*([A-Z0-9\-]+)', re.IGNORECASE)
    
    BRANDS = ["Huawei", "Cisco", "ZTE", "Mikrotik", "TP-Link", "Nokia"]
    
    def detect_transaction_type(self, text):
        text_lower = text.lower()
        if any(k in text_lower for k in ["rekap", "report", "laporan"]):
            return "rekap"
        if any(k in text_lower for k in ["so", "stock opname", "opname"]):
            return "so"
        if any(k in text_lower for k in ["keluar", "ambil", "pakai", "kebutuhan", "digunakan", "kirim"]):
            return "keluar"
        if any(k in text_lower for k in ["masuk", "terima", "sisaan", "diterima"]):
            return "masuk"
        return "unknown"
    
    def extract_brand(self, text):
        text_clean = text.lower()
        for brand in self.BRANDS:
            if brand.lower() in text_clean:
                return brand
        return None
    
    def extract_quantity(self, text):
        match = self.QUANTITY_PATTERN.search(text)
        if match:
            return int(match.group(1)), match.group(2).lower()
        return 1, "pcs"
    
    def extract_serial_numbers(self, text):
        matches = self.SERIAL_PATTERN.findall(text)
        return [m.strip().upper() for m in matches if len(m.strip()) > 3]
    
    def parse_bullet_items(self, text):
        items = []
        bullet_pattern = re.compile(r'^[\s]*[•\-\*]\s+(.+)$', re.MULTILINE)
        bullet_matches = bullet_pattern.findall(text)
        
        if bullet_matches:
            for line in bullet_matches:
                item = self.parse_single_item(line)
                if item:
                    items.append(item)
        else:
            lines = [l.strip() for l in text.split('\n') if l.strip() and not l.strip().startswith(('kebutuhan', 'sisaan', 'so', '{so'))]
            for line in lines:
                if '-' in line[:2]:
                    item = self.parse_single_item(line[1:].strip())
                    if item:
                        items.append(item)
        
        return items
    
    def parse_single_item(self, text):
        text = text.strip()
        if not text or len(text) < 3:
            return None
        
        qty, unit = self.extract_quantity(text)
        brand = self.extract_brand(text)
        serials = self.extract_serial_numbers(text)
        
        # Clean name
        name = text
        qty_match = self.QUANTITY_PATTERN.search(name)
        if qty_match:
            name = name.replace(qty_match.group(0), "").strip()
        
        for sn in serials:
            name = re.sub(rf'(?i)sn[:\s]*{re.escape(sn)}', '', name)
        
        name = re.sub(r'\[.*?\]', '', name)
        name = re.sub(r'\(.*?\)', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        name = name.strip('•-*,.:;')
        
        if len(name) < 3:
            name = text[:100]
        
        return ParsedItem(
            name=name,
            brand=brand,
            quantity=qty,
            unit=unit,
            serial_numbers=serials
        )
    
    def parse_message(self, text):
        trans_type = self.detect_transaction_type(text)
        
        if trans_type == "rekap":
            return ParsedTransaction(type="rekap", items=[])
        
        purpose = None
        dest_match = re.search(r'(?:ke|untuk|kebutuhan|project|branch)\s+([^.\n]+)', text, re.IGNORECASE)
        if dest_match:
            purpose = dest_match.group(1).strip()
        
        items = self.parse_bullet_items(text)
        
        return ParsedTransaction(
            type=trans_type,
            items=items,
            purpose=purpose
        )

def main():
    test_messages = [
        """Kebutuhan migrasi server unit JTB
- DCDU 12B huawei (1 unit)
SN: 21021207316TL4922814 
- batterai ZTE (2 unit)""",
        
        """sisaan BOQ jatibarang > rajak
- tiang 3inch 7m Biasa (25 Btg)""",
        
        """SO 15 Maret 2026
Data Sfp
•Huawei 155Mbps 15Km 1310 Nm (2pcs)""",
    ]
    
    parser = MessageParser()
    
    print("=" * 60)
    print("WAREHOUSE BOT - PARSER DEMO")
    print("=" * 60)
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"TEST #{i}")
        print(f"{'='*60}")
        print(f"INPUT:\n{msg[:80]}...")
        print(f"\n--- PARSED ---")
        
        result = parser.parse_message(msg)
        
        print(f"Type: {result.type.upper()}")
        if result.purpose:
            print(f"Purpose/Dest: {result.purpose}")
        
        print(f"\nItems ({len(result.items)}):")
        for j, item in enumerate(result.items, 1):
            print(f"  {j}. {item.name}")
            print(f"     Brand: {item.brand or '-'}")
            print(f"     Qty: {item.quantity} {item.unit}")
            if item.serial_numbers:
                print(f"     SN: {', '.join(item.serial_numbers)}")
    
    print("\n" + "=" * 60)
    print("Demo complete! Parser is working.")
    print("=" * 60)

if __name__ == "__main__":
    main()
