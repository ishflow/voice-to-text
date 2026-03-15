"""
Voice to Text App - Build Script
PyInstaller ile tek .exe dosyasi olusturur.
"""

import subprocess
import sys
import os

def build():
    """PyInstaller ile .exe olustur."""

    # PyInstaller kurulu mu kontrol et
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller kuruluyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Build komutu
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Tek dosya
        "--windowed",          # Konsol penceresi yok
        "--name", "VoiceToText",  # Dosya adi
        "--icon", "icon.ico",  # Uygulama ikonu
        "--add-data", "config.py;.",  # Config dosyasini dahil et
        "--hidden-import", "pystray._win32",
        "--hidden-import", "PIL._tkinter_finder",
        "main.py"
    ]

    print("Build basliyor...")
    print(f"Komut: {' '.join(cmd)}")

    subprocess.check_call(cmd)

    print("\n" + "="*50)
    print("BUILD TAMAMLANDI!")
    print("="*50)
    print(f"\nDosya konumu: dist/VoiceToText.exe")
    print("\nKullanim:")
    print("1. dist/VoiceToText.exe dosyasini istediginiz yere kopyalayin")
    print("2. Calistirin - ilk seferde API key soracak")
    print("3. API key .env dosyasina kaydedilecek")

if __name__ == "__main__":
    build()
