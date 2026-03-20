@echo off
chcp 65001 >nul 2>&1
title Voice to Text - Kurulum

echo.
echo  ══════════════════════════════════════════
echo   Voice to Text + Instant Translate Setup
echo  ══════════════════════════════════════════
echo.

:: Python kontrolu
python --version >nul 2>&1
if errorlevel 1 (
    echo  [HATA] Python bulunamadi!
    echo  Python 3.11+ yukleyin: https://python.org/downloads
    echo.
    pause
    exit /b 1
)

echo  [1/3] Python bulundu:
python --version
echo.

:: Virtual environment
echo  [2/3] Sanal ortam olusturuluyor...
if not exist "venv" (
    python -m venv venv
    echo        venv olusturuldu.
) else (
    echo        venv zaten mevcut.
)
echo.

:: Bagimliliklari yukle
echo  [3/3] Bagimliliklar yukleniyor...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
echo        Bagimliliklar yuklendi.
echo.

:: .env dosyasi
if not exist ".env" (
    copy .env.example .env >nul
    echo  [!] .env dosyasi olusturuldu.
    echo      Ilk calistirmada ayarlardan API key girebilirsiniz.
) else (
    echo  [OK] .env dosyasi zaten mevcut.
)

echo.
echo  ══════════════════════════════════════════
echo   Kurulum tamamlandi!
echo  ══════════════════════════════════════════
echo.
echo   Calistirmak icin:
echo     start.bat
echo.
echo   Veya manuel:
echo     venv\Scripts\pythonw.exe main.py
echo.
pause
