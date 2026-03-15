"""
Voice to Text App - Installer Builder
Kurulum dosyasini olusturur (VoiceToText.exe icinde gomulu)
"""

import subprocess
import sys
import os

def build():
    """Installer .exe olustur."""

    # Build komutu - VoiceToText.exe'yi data olarak ekle
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "VoiceToText_Setup",
        "--icon", "icon.ico",
        "--add-data", "dist/VoiceToText.exe;.",
        "installer.py"
    ]

    print("Installer build basliyor...")
    print(f"Komut: {' '.join(cmd)}")

    subprocess.check_call(cmd)

    print("\n" + "="*50)
    print("INSTALLER BUILD TAMAMLANDI!")
    print("="*50)
    print(f"\nDosya: dist/VoiceToText_Setup.exe")
    print("\nBu dosyayi dagitabilirsiniz.")
    print("Kurulum sihirbazi:")
    print("- Masaustune kisayol ekler")
    print("- Baslat menusune ekler")
    print("- Opsiyonel: Windows ile baslat")

if __name__ == "__main__":
    build()
