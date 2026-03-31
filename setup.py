#!/usr/bin/env python3
"""
Setup script untuk Warehouse Telegram Bot
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        sys.exit(1)
    print("✅ Python version OK")

def check_tesseract():
    """Check if Tesseract is installed"""
    import subprocess
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract OCR installed")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  Tesseract OCR tidak ditemukan!")
    print("   Install dengan:")
    print("   Ubuntu/Debian: sudo apt install tesseract-ocr")
    print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    return False

def create_env_file():
    """Create .env file if not exists"""
    env_path = Path('.env')
    env_example = Path('.env.example')
    
    if env_path.exists():
        print("✅ .env file exists")
        return
    
    if env_example.exists():
        print("📝 Creating .env from example...")
        env_path.write_text(env_example.read_text())
        print("⚠️  Please edit .env with your BOT_TOKEN!")
    else:
        print("❌ .env.example not found")

def create_directories():
    """Create necessary directories"""
    dirs = ['data', 'reports', 'temp']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        print(f"✅ {d}/ directory ready")

def main():
    """Main setup"""
    print("🔧 Warehouse Bot Setup\n")
    
    check_python_version()
    check_tesseract()
    create_directories()
    create_env_file()
    
    print("\n📦 Installing dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env with your BOT_TOKEN (from @BotFather)")
    print("2. Edit ADMIN_IDS with your Telegram user ID")
    print("3. Run: python bot.py")
    print("\nOr with Docker:")
    print("   docker-compose up -d")

if __name__ == "__main__":
    main()
