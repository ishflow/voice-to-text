"""
Voice to Text - Kurulum
"""
import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import time

APP_NAME = "Voice to Text"
APP_EXE = "VoiceToText.exe"


class Installer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice to Text Kurulum")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")

        # Ortala
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 500) // 2
        y = (self.root.winfo_screenheight() - 400) // 2
        self.root.geometry(f"+{x}+{y}")

        self.desktop_var = tk.BooleanVar(value=True)
        self.startmenu_var = tk.BooleanVar(value=True)
        self.startup_var = tk.BooleanVar(value=False)
        self.launch_var = tk.BooleanVar(value=True)
        self.exe_path = None

        self.page1()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def page1(self):
        """Hosgeldin"""
        self.clear()

        # Ust bosluk
        tk.Label(self.root, text="", bg="#1e1e1e").pack(pady=15)

        # Logo - mor daire
        c = tk.Canvas(self.root, width=80, height=80, bg="#1e1e1e", highlightthickness=0)
        c.pack()
        c.create_oval(5, 5, 75, 75, fill="#8b5cf6", outline="")
        c.create_rectangle(30, 18, 50, 45, fill="white", outline="")
        c.create_arc(22, 35, 58, 60, start=0, extent=-180, outline="white", width=3, style="arc")
        c.create_line(40, 55, 40, 68, fill="white", width=3)
        c.create_line(28, 68, 52, 68, fill="white", width=3)

        # Baslik
        tk.Label(self.root, text="Voice to Text", font=("Segoe UI", 26, "bold"),
                bg="#1e1e1e", fg="white").pack(pady=(15,5))

        tk.Label(self.root, text="v1.0", font=("Segoe UI", 10),
                bg="#1e1e1e", fg="#666").pack()

        tk.Label(self.root, text="Ctrl+Space ile ses kaydı başlatın\nMetin otomatik yapıştırılır",
                font=("Segoe UI", 11), bg="#1e1e1e", fg="#aaa", justify="center").pack(pady=20)

        # BUTONLAR - alt kisimda sabit
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=30)

        # Iptal butonu
        btn_iptal = tk.Button(btn_frame, text="İptal", font=("Segoe UI", 11),
                             bg="#444", fg="white", width=12, pady=8,
                             relief="flat", command=self.root.quit)
        btn_iptal.pack(side="left", padx=10)

        # Ileri butonu
        btn_ileri = tk.Button(btn_frame, text="İleri →", font=("Segoe UI", 11, "bold"),
                             bg="#8b5cf6", fg="white", width=12, pady=8,
                             relief="flat", command=self.page2)
        btn_ileri.pack(side="left", padx=10)

    def page2(self):
        """Secenekler"""
        self.clear()

        tk.Label(self.root, text="", bg="#1e1e1e").pack(pady=20)

        tk.Label(self.root, text="Kurulum Seçenekleri", font=("Segoe UI", 22, "bold"),
                bg="#1e1e1e", fg="white").pack(pady=(0,30))

        # Checkboxlar
        tk.Checkbutton(self.root, text="  Masaüstüne kısayol oluştur",
                      variable=self.desktop_var, font=("Segoe UI", 11),
                      bg="#1e1e1e", fg="white", selectcolor="#333",
                      activebackground="#1e1e1e", activeforeground="white").pack(anchor="w", padx=80, pady=5)

        tk.Checkbutton(self.root, text="  Başlat menüsüne ekle",
                      variable=self.startmenu_var, font=("Segoe UI", 11),
                      bg="#1e1e1e", fg="white", selectcolor="#333",
                      activebackground="#1e1e1e", activeforeground="white").pack(anchor="w", padx=80, pady=5)

        tk.Checkbutton(self.root, text="  Windows ile birlikte başlat",
                      variable=self.startup_var, font=("Segoe UI", 11),
                      bg="#1e1e1e", fg="white", selectcolor="#333",
                      activebackground="#1e1e1e", activeforeground="white").pack(anchor="w", padx=80, pady=5)

        # Kurulum yolu
        path = Path(os.environ.get("LOCALAPPDATA", "")) / "VoiceToText"
        tk.Label(self.root, text=f"Konum: {path}", font=("Segoe UI", 9),
                bg="#1e1e1e", fg="#555").pack(pady=(30,0))

        # Butonlar
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=30)

        tk.Button(btn_frame, text="← Geri", font=("Segoe UI", 11),
                 bg="#444", fg="white", width=12, pady=8,
                 relief="flat", command=self.page1).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Kur", font=("Segoe UI", 11, "bold"),
                 bg="#22c55e", fg="white", width=12, pady=8,
                 relief="flat", command=self.page3).pack(side="left", padx=10)

    def page3(self):
        """Kurulum"""
        self.clear()

        tk.Label(self.root, text="", bg="#1e1e1e").pack(pady=40)

        tk.Label(self.root, text="Kuruluyor...", font=("Segoe UI", 22, "bold"),
                bg="#1e1e1e", fg="white").pack(pady=(0,20))

        self.status = tk.Label(self.root, text="Hazırlanıyor...", font=("Segoe UI", 11),
                              bg="#1e1e1e", fg="#888")
        self.status.pack(pady=10)

        # Progress
        style = ttk.Style()
        style.theme_use('default')
        style.configure("g.Horizontal.TProgressbar", troughcolor='#333', background='#22c55e')

        self.prog = ttk.Progressbar(self.root, length=300, style="g.Horizontal.TProgressbar")
        self.prog.pack(pady=15)

        self.pct = tk.Label(self.root, text="0%", font=("Segoe UI", 14, "bold"),
                           bg="#1e1e1e", fg="#22c55e")
        self.pct.pack()

        self.root.after(300, self.install)

    def install(self):
        """Kurulum yap"""
        success = False
        try:
            # Process kapat
            self.upd("Hazırlanıyor...", 10)
            subprocess.run(['taskkill', '/F', '/IM', APP_EXE], capture_output=True)
            time.sleep(0.5)

            # Kaynak
            if getattr(sys, 'frozen', False):
                src = Path(sys._MEIPASS) / APP_EXE
            else:
                src = Path(__file__).parent / "dist" / APP_EXE

            # Hedef
            self.upd("Klasör oluşturuluyor...", 25)
            dst_dir = Path(os.environ["LOCALAPPDATA"]) / "VoiceToText"
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = dst_dir / APP_EXE

            # Kopyala
            self.upd("Dosya kopyalanıyor...", 50)
            if dst.exists():
                dst.unlink()
            shutil.copy2(src, dst)
            self.exe_path = dst

            # Kisayollar
            if self.desktop_var.get():
                self.upd("Masaüstü kısayolu...", 65)
                self.shortcut(dst, Path.home() / "Desktop" / "Voice to Text.lnk")

            if self.startmenu_var.get():
                self.upd("Başlat menüsü...", 80)
                sm = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs"
                self.shortcut(dst, sm / "Voice to Text.lnk")

            if self.startup_var.get():
                self.upd("Başlangıç...", 90)
                su = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup"
                self.shortcut(dst, su / "Voice to Text.lnk")

            self.upd("Tamamlandı!", 100)
            success = True

        except Exception as e:
            self.status.config(text=f"Hata: {e}", fg="#ef4444")

        self.root.after(500, lambda: self.page4(success))

    def shortcut(self, target, lnk):
        ps = f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{lnk}");$s.TargetPath="{target}";$s.Save()'
        subprocess.run(['powershell', '-Command', ps], capture_output=True)

    def upd(self, msg, pct):
        self.status.config(text=msg)
        self.prog["value"] = pct
        self.pct.config(text=f"{pct}%")
        self.root.update()
        time.sleep(0.2)

    def page4(self, success):
        """Bitis"""
        self.clear()

        tk.Label(self.root, text="", bg="#1e1e1e").pack(pady=30)

        if success:
            # Yesil tik
            c = tk.Canvas(self.root, width=70, height=70, bg="#1e1e1e", highlightthickness=0)
            c.pack()
            c.create_oval(5, 5, 65, 65, fill="#22c55e", outline="")
            c.create_line(20, 35, 30, 45, fill="white", width=4)
            c.create_line(30, 45, 50, 25, fill="white", width=4)

            tk.Label(self.root, text="Kurulum Tamamlandı!", font=("Segoe UI", 22, "bold"),
                    bg="#1e1e1e", fg="#22c55e").pack(pady=(15,10))

            tk.Label(self.root, text="Voice to Text başarıyla kuruldu.\nCtrl+Space ile kayıt başlatın.",
                    font=("Segoe UI", 11), bg="#1e1e1e", fg="#aaa", justify="center").pack(pady=10)

            tk.Checkbutton(self.root, text="  Uygulamayı şimdi başlat",
                          variable=self.launch_var, font=("Segoe UI", 11),
                          bg="#1e1e1e", fg="white", selectcolor="#333",
                          activebackground="#1e1e1e", activeforeground="white").pack(pady=15)
        else:
            # Kirmizi X
            c = tk.Canvas(self.root, width=70, height=70, bg="#1e1e1e", highlightthickness=0)
            c.pack()
            c.create_oval(5, 5, 65, 65, fill="#ef4444", outline="")
            c.create_line(22, 22, 48, 48, fill="white", width=4)
            c.create_line(48, 22, 22, 48, fill="white", width=4)

            tk.Label(self.root, text="Kurulum Başarısız", font=("Segoe UI", 22, "bold"),
                    bg="#1e1e1e", fg="#ef4444").pack(pady=(15,10))

            tk.Label(self.root, text="Bir hata oluştu.",
                    font=("Segoe UI", 11), bg="#1e1e1e", fg="#aaa").pack(pady=10)

        # Bitir butonu
        tk.Button(self.root, text="Bitir", font=("Segoe UI", 11, "bold"),
                 bg="#8b5cf6", fg="white", width=14, pady=8,
                 relief="flat", command=lambda: self.finish(success)).pack(pady=30)

    def finish(self, success):
        if success and self.launch_var.get() and self.exe_path:
            os.startfile(self.exe_path)
        self.root.quit()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Installer().run()
