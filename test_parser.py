#!/usr/bin/env python3
"""
Test script for message parser
"""

from parser import MessageParser, format_item_summary

# Test cases
test_messages = [
    # Barang keluar example
    """Kebutuhan migrasi server unit JTB
- DCDU 12B huawei  (1 unit)
SN: 21021207316TL4922814 
- batterai ZTE ZXDC48 FB100B3 (1 unit)
SN: 219502212702
- rekti huawei EPS75 4815AF
SN : 21 04296MC9000108
- kabel 10mm (2 gulung)
- Solasi Nasional (1 pcs)

Tim Project
- solasi Nasional (1 pcs)

Branch Brebes mas udin
- batterai PJUTS (2 unit)""",

    # Barang masuk example
    """*barang masuk*
sisaan BOQ jatibarang > rajak
- tiang 3inch 7m Biasa (25 Btg)""",

    # SO example (partial)
    """{SO 15 Maret 2026}

∆Data Sfp
SFP MultiMode (MM)
•Huawei 155Mbps 15Km 1310 Nm (2pcs)
•Fiberson 1G 550M 850Nm (1pcs)
•Cisco 1G 550M 850Nm (7pcs)""",

    # Simple
    "sisaan BOQ cirebon - SFP Huawei 10G 10km (5 pcs) SN: 21021207316TL4922814",
    
    # Without explicit type
    "Ambil dari gudang: Router Cisco 1 unit untuk install JTB",
]

def test_parser():
    parser = MessageParser()
    
    print("=" * 60)
    print("🧪 Testing Message Parser")
    print("=" * 60)
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"Test #{i}")
        print(f"{'='*60}")
        print(f"Input:\n{msg[:100]}...")
        print(f"\n--- Parsed ---")
        
        result = parser.parse_message(msg)
        
        print(f"Type: {result.type}")
        if result.purpose:
            print(f"Purpose: {result.purpose}")
        if result.destination:
            print(f"Destination: {result.destination}")
        
        print(f"\nItems ({len(result.items)}):")
        for j, item in enumerate(result.items, 1):
            print(f"\n  {j}. {item.name}")
            print(f"     Brand: {item.brand}")
            print(f"     Qty: {item.quantity} {item.unit}")
            print(f"     Specs: {item.specs}")
            print(f"     SNs: {item.serial_numbers}")
            print(f"     Category: {item.category}")

if __name__ == '__main__':
    test_parser()
