#!/usr/bin/env python3
"""
Pre-flight check script - verify all dependencies before running
"""

import sys
import os
from pathlib import Path

def check_python():
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor} (need 3.9+)")
        return False

def check_dependencies():
    print("\nChecking Python dependencies...")
    required = {
        'aiogram': 'Telegram bot framework',
        'sqlalchemy': 'Database ORM',
        'pytesseract': 'OCR',
        'PIL': 'Image processing',
        'cv2': 'OpenCV',
        'pandas': 'Data processing',
    }
    
    all_ok = True
    for module, purpose in required.items():
        try:
            if module == 'PIL':
                __import__('PIL')
            elif module == 'cv2':
                __import__('cv2')
            else:
                __import__(module)
            print(f"  ✅ {module} ({purpose})")
        except ImportError:
            print(f"  ❌ {module} missing - {purpose}")
            all_ok = False
    
    return all_ok

def check_tesseract():
    print("\nChecking Tesseract OCR...")
    import shutil
    tesseract_cmd = os.getenv('TESSERACT_CMD', 'tesseract')
    
    if shutil.which(tesseract_cmd):
        try:
            import subprocess
            result = subprocess.run([tesseract_cmd, '--version'], 
                                  capture_output=True, text=True)
            version = result.stdout.split('\n')[0]
            print(f"  ✅ Tesseract found: {version[:50]}")
            return True
        except:
            print(f"  ⚠️  Tesseract found but error running")
            return True  # Still usable
    else:
        print(f"  ❌ Tesseract not found in PATH")
        print(f"     Install: sudo apt install tesseract-ocr (Linux)")
        print(f"     Or download: https://github.com/UB-Mannheim/tesseract/wiki (Windows)")
        return False

def check_env():
    print("\nChecking environment...")
    env_path = Path('.env')
    env_example = Path('.env.example')
    
    if env_path.exists():
        print("  ✅ .env file found")
        # Check critical vars
        with open(env_path) as f:
            content = f.read()
            if 'your_bot_token_here' in content:
                print("  ⚠️  BOT_TOKEN not configured (still default)")
                return False
            if 'BOT_TOKEN=' in content and len(content.split('BOT_TOKEN=')[1].split('\n')[0].strip()) > 20:
                print("  ✅ BOT_TOKEN configured")
            if '123456789' in content:
                print("  ⚠️  ADMIN_IDS using default (change to your ID)")
        return True
    else:
        if env_example.exists():
            print("  ❌ .env not found (but .env.example exists)")
            print("     Run: cp .env.example .env")
            print("     Then edit .env with your BOT_TOKEN")
        else:
            print("  ❌ No .env file found")
        return False

def check_directories():
    print("\nChecking directories...")
    dirs = ['data', 'reports', 'temp']
    all_ok = True
    for d in dirs:
        path = Path(d)
        if path.exists():
            print(f"  ✅ {d}/")
        else:
            print(f"  ⚠️  {d}/ not found, creating...")
            path.mkdir(exist_ok=True)
    return all_ok

def test_parser():
    print("\nTesting parser...")
    try:
        from parser import MessageParser
        parser = MessageParser()
        test = "Kebutuhan test - SFP Huawei 10G (2 pcs) SN: TEST123"
        result = parser.parse_message(test)
        if result.items:
            print(f"  ✅ Parser working ({len(result.items)} items detected)")
            return True
        else:
            print(f"  ⚠️  Parser running but no items detected")
            return True
    except Exception as e:
        print(f"  ❌ Parser error: {e}")
        return False

def main():
    print("=" * 60)
    print("WAREHOUSE BOT - PRE-FLIGHT CHECK")
    print("=" * 60)
    
    checks = [
        ("Python", check_python),
        ("Dependencies", check_dependencies),
        ("Tesseract OCR", check_tesseract),
        ("Environment", check_env),
        ("Directories", check_directories),
        ("Parser", test_parser),
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ Error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    critical = ['Python', 'Environment']
    critical_ok = all(r for n, r in results if n in critical)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print("\n" + "=" * 60)
    if critical_ok:
        print("✅ READY TO RUN")
        print("   Run: python bot.py")
        print("   Or:  docker-compose up -d")
    else:
        print("❌ FIX ISSUES ABOVE BEFORE RUNNING")
    print("=" * 60)

if __name__ == "__main__":
    main()
