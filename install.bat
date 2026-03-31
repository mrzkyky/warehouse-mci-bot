@echo off
chcp 65001 >nul
echo ==========================================
echo WAREHOUSE BOT - WINDOWS INSTALLER
echo ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found! Install from python.org
    pause
    exit /b 1
)
echo [OK] Python found

:: Create directories
echo.
echo [..] Creating directories...
if not exist data mkdir data
if not exist reports mkdir reports
if not exist temp mkdir temp
echo [OK] Directories ready

:: Install dependencies
echo.
echo [..] Installing dependencies... (this may take a while)
pip install -r requirements.txt
if errorlevel 1 (
    echo [X] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

:: Setup .env
echo.
if not exist .env (
    echo [..] Creating .env file...
    copy .env.example .env
    echo [!] IMPORTANT: Edit .env with your BOT_TOKEN!
    echo     Get token from @BotFather on Telegram
) else (
    echo [OK] .env already exists
)

:: Check Tesseract
echo.
echo [..] Checking Tesseract OCR...
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo [!] Tesseract not found - Download from:
    echo     https://github.com/UB-Mannheim/tesseract/wiki
    echo     (Optional - only needed for SN scanning)
) else (
    echo [OK] Tesseract found
)

:: Test parser
echo.
echo [..] Testing parser...
python demo.py

:: Done
echo.
echo ==========================================
echo INSTALLATION COMPLETE!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env with your BOT_TOKEN
echo 2. Run: python bot.py
echo.
echo Or with Docker:
echo    docker-compose up -d
echo.
pause
