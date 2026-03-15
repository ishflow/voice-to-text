"""
Voice to Text App v2.0
======================
ALT cift tiklama ile aktif olan, Whisper API ile Turkce ses tanima yapan
basit ve hizli bir Windows uygulamasi.

Kullanim:
    1. Uygulamayi baslatin (system tray'de gorunecek)
    2. ALT'a 2 kez hizlica basin -> Kayit baslar
    3. Turkce konusun
    4. ALT'a 2 kez tekrar basin -> Kayit durur
    5. Metin otomatik olarak aktif pencereye yapistirtilir
"""

import sys
import os
import io
import ctypes
from ctypes import wintypes
import math
import random

# Windows console encoding fix (sadece konsol varsa)
if sys.platform == 'win32' and sys.stdout is not None:
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        pass  # Konsol yok, PyInstaller --windowed modunda

import time
import wave
import threading
import tkinter as tk
from tkinter import messagebox
import numpy as np

import sounddevice as sd
from scipy.io import wavfile
import pyperclip
import pyautogui
import pystray
from PIL import Image, ImageDraw
from pynput import keyboard
from openai import OpenAI

import config


def enable_blur_effect(hwnd):
    """Windows Acrylic/Blur efektini etkinlestir."""
    try:
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_uint),
                ("AccentFlags", ctypes.c_uint),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_uint),
            ]

        class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ACCENT_POLICY)),
                ("SizeOfData", ctypes.c_size_t),
            ]

        accent = ACCENT_POLICY()
        accent.AccentState = 4  # ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = 2
        accent.GradientColor = 0x99FFFFFF

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = ctypes.sizeof(accent)

        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.pointer(data))
        return True
    except Exception:
        return False


class AudioRecorder:
    """Mikrofon ses kaydi yoneticisi."""

    def __init__(self):
        self.frames = []
        self.is_recording = False
        self.recording_thread = None

    def start_recording(self):
        """Ses kaydini baslat."""
        if self.is_recording:
            return
        self.frames = []
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()

    def _record(self):
        """Kayit dongusu (ayri thread'de calisir)."""
        try:
            def callback(indata, frames, time_info, status):
                if status:
                    print(f"Kayit durumu: {status}")
                if self.is_recording:
                    self.frames.append(indata.copy())

            with sd.InputStream(
                samplerate=config.SAMPLE_RATE,
                channels=config.CHANNELS,
                dtype='int16',
                callback=callback,
                blocksize=config.CHUNK_SIZE
            ):
                start_time = time.time()
                while self.is_recording:
                    if time.time() - start_time > config.MAX_RECORDING_DURATION:
                        self.is_recording = False
                        break
                    time.sleep(0.1)
        except Exception as e:
            print(f"Kayit hatasi: {e}")
            self.is_recording = False

    def stop_recording(self) -> str:
        """Ses kaydini durdur ve dosya yolunu dondur."""
        if not self.is_recording and not self.frames:
            return None
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
        if not self.frames:
            return None

        audio_data = np.concatenate(self.frames, axis=0)
        duration = len(audio_data) / config.SAMPLE_RATE
        print(f"Kayit suresi: {duration:.2f} saniye, {len(self.frames)} frame")

        wav_path = config.TEMP_AUDIO_FILE
        wavfile.write(wav_path, config.SAMPLE_RATE, audio_data)
        return wav_path

    def cleanup(self):
        """Kaynaklari temizle."""
        self.is_recording = False
        self.frames = []


class WhisperTranscriber:
    """OpenAI Whisper API ile ses-metin donusturucu."""

    def __init__(self):
        if not config.OPENAI_API_KEY:
            raise ValueError(config.MSG_NO_API_KEY)
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def transcribe(self, audio_path: str, language: str = None) -> str:
        """Ses dosyasini metne donustur."""
        try:
            with open(audio_path, "rb") as audio_file:
                params = {"model": config.WHISPER_MODEL, "file": audio_file}
                if language:
                    params["language"] = language
                response = self.client.audio.transcriptions.create(**params)
            return response.text
        except Exception as e:
            print(f"Transcription hatasi: {e}")
            raise


class FloatingIndicator:
    """Minimal siyah gosterge — nokta + dalga + timer."""

    # Durum renkleri
    COLOR_RECORDING = "#FF3B30"   # Kirmizi — kayit
    COLOR_PROCESSING = "#FF9500"  # Turuncu — isliyor
    COLOR_SUCCESS = "#30D158"     # Yesil — yapistirdi
    BAR_COLOR = "#3a3a3c"         # Koyu gri barlar

    def __init__(self, recorder=None):
        self.root = None
        self.canvas = None
        self._is_visible = False
        self.recording_start_time = None
        self.timer_running = False
        self.wave_bars = []
        self.bar_heights = []
        self.recorder = recorder
        self.num_bars = 24
        self.phase = 0.0
        self.pulse_phase = 0.0
        self.timer_text = None
        self.record_dot = None
        self.on_cancel = None  # Iptal callback

    def set_recorder(self, recorder):
        self.recorder = recorder

    def show(self, message: str):
        if self.root is None:
            self._create_window()

        self.recording_start_time = time.time()
        self.timer_running = True
        self.bar_heights = [2.0] * self.num_bars
        self.phase = 0.0
        self.pulse_phase = 0.0

        # Kayit durumuna resetle
        if self.record_dot:
            self.canvas.itemconfig(self.record_dot, fill=self.COLOR_RECORDING)
        if self.timer_text:
            self.canvas.itemconfig(self.timer_text, fill="#8e8e93")
        for bar in self.wave_bars:
            self.canvas.itemconfig(bar, fill=self.BAR_COLOR)

        if not self._is_visible:
            self.root.deiconify()
            self._is_visible = True

        self._update_timer()
        self._animate()
        self.root.update()

    def hide(self):
        self.timer_running = False
        if self.root and self._is_visible:
            self.root.withdraw()
            self._is_visible = False

    def update_message(self, message: str):
        self.timer_running = False
        if not self.canvas:
            return

        if "Tamam" in message:
            color = self.COLOR_SUCCESS
        elif "Hata" in message:
            color = "#FF3B30"
        else:
            # Isleniyor — turuncu
            color = self.COLOR_PROCESSING

        if self.record_dot:
            self.canvas.itemconfig(self.record_dot, fill=color)
        self.root.update()

    def _get_audio_level(self):
        if self.recorder and self.recorder.frames:
            try:
                last_frame = self.recorder.frames[-1]
                arr = np.frombuffer(last_frame, dtype=np.int16)
                return min(np.abs(arr).mean() / 3000, 1.0)
            except Exception:
                pass
        return 0.03

    def _update_timer(self):
        if not self.timer_running or not self._is_visible:
            return
        elapsed = time.time() - self.recording_start_time
        m, s = int(elapsed // 60), int(elapsed % 60)
        if self.timer_text:
            self.canvas.itemconfig(self.timer_text, text=f"{m}:{s:02d}")
        if self.root:
            self.root.after(100, self._update_timer)

    def _animate(self):
        if not self.timer_running or not self._is_visible:
            return

        audio = self._get_audio_level()
        self.phase += 0.1
        self.pulse_phase += 0.06

        # Kayit noktasi pulse — kirmizi nefes alir
        p = 0.5 + 0.5 * math.sin(self.pulse_phase)
        r = 255
        g = int(59 + 30 * p)
        b = int(48 + 30 * p)
        if self.record_dot:
            self.canvas.itemconfig(self.record_dot, fill=f"#{r:02x}{g:02x}{b:02x}")

        # Ses dalgasi
        self.bar_heights.pop(0)
        base = 2 + audio * 16
        wave = math.sin(self.phase) * 2.5
        new_h = max(1.5, (base + wave) * random.uniform(0.7, 1.3))
        self.bar_heights.append(new_h)

        start_x = 48
        cy = 28
        gap = 5.0
        bw = 2.5

        for i, bar in enumerate(self.wave_bars):
            h = self.bar_heights[i]
            x = start_x + i * gap
            self.canvas.coords(bar, x, cy - h, x + bw, cy + h)

            # Ses seviyesine gore koyu gri → biraz daha acik gri
            t = min(1.0, h / 18)
            c = int(58 + 30 * t)  # #3a3a3c → #585858
            self.canvas.itemconfig(bar, fill=f"#{c:02x}{c:02x}{c:02x}")

        if self.root:
            self.root.after(50, self._animate)

    def _create_window(self):
        self.root = tk.Tk()
        self.root.title("")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        w, h = 280, 56

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = sh - h - 80

        self.root.geometry(f"{w}x{h}+{x}+{y}")

        chroma = "#010101"
        self.root.configure(bg=chroma)
        self.root.attributes("-transparentcolor", chroma)
        self.root.attributes("-alpha", 0.92)

        # Surukleme state
        self._drag_x = 0
        self._drag_y = 0

        self.canvas = tk.Canvas(
            self.root, width=w, height=h,
            bg=chroma, highlightthickness=0,
        )
        self.canvas.pack()

        # Pill shape — siyah govde, cok ince koyu gri border
        self._pill(1, 1, w - 1, h - 1, 28,
                   fill="#0a0a0a", outline="#2c2c2e", width=1)

        # Kayit noktasi — buyukce
        dot_cx, dot_cy = 24, h // 2
        dot_r = 8
        self.record_dot = self.canvas.create_oval(
            dot_cx - dot_r, dot_cy - dot_r,
            dot_cx + dot_r, dot_cy + dot_r,
            fill=self.COLOR_RECORDING, outline="", width=0,
        )

        # Ses dalgasi barlari
        start_x = 48
        cy = h // 2
        gap = 5.0
        bw = 2.5

        self.wave_bars = []
        self.bar_heights = [2.0] * self.num_bars
        for i in range(self.num_bars):
            bx = start_x + i * gap
            bar = self.canvas.create_rectangle(
                bx, cy - 2, bx + bw, cy + 2,
                fill=self.BAR_COLOR, outline="", width=0,
            )
            self.wave_bars.append(bar)

        # Timer
        self.timer_text = self.canvas.create_text(
            w - 52, h // 2,
            text="0:00",
            font=("Segoe UI Semibold", 11),
            fill="#8e8e93", anchor="e",
        )

        # Ince ayirici cizgi
        self.canvas.create_line(
            w - 42, 14, w - 42, h - 14,
            fill="#2c2c2e", width=1,
        )

        # X (iptal) butonu
        cx_btn = w - 22
        cy_btn = h // 2
        sz = 6  # X cizgi boyutu
        self.x_line1 = self.canvas.create_line(
            cx_btn - sz, cy_btn - sz, cx_btn + sz, cy_btn + sz,
            fill="#636366", width=2, capstyle="round",
        )
        self.x_line2 = self.canvas.create_line(
            cx_btn - sz, cy_btn + sz, cx_btn + sz, cy_btn - sz,
            fill="#636366", width=2, capstyle="round",
        )
        # X hover alani (gorunmez dikdortgen)
        self.x_hit = self.canvas.create_rectangle(
            cx_btn - 14, cy_btn - 14, cx_btn + 14, cy_btn + 14,
            fill="", outline="", width=0,
        )
        self.canvas.tag_bind(self.x_hit, "<Enter>", self._on_x_hover_in)
        self.canvas.tag_bind(self.x_hit, "<Leave>", self._on_x_hover_out)
        self.canvas.tag_bind(self.x_hit, "<ButtonRelease-1>", self._on_x_click)
        # X cizimleri de tiklanabilir
        self.canvas.tag_bind(self.x_line1, "<ButtonRelease-1>", self._on_x_click)
        self.canvas.tag_bind(self.x_line2, "<ButtonRelease-1>", self._on_x_click)

        # Surukleme icin mouse event'leri
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_move)

        self.root.withdraw()

    def _on_x_hover_in(self, event):
        """X uzerine gelince kirmiziya don."""
        self.canvas.itemconfig(self.x_line1, fill="#FF453A")
        self.canvas.itemconfig(self.x_line2, fill="#FF453A")

    def _on_x_hover_out(self, event):
        """X'ten ayrilinca griye don."""
        self.canvas.itemconfig(self.x_line1, fill="#636366")
        self.canvas.itemconfig(self.x_line2, fill="#636366")

    def _on_x_click(self, event):
        """X'e tiklaninca kaydi iptal et."""
        if self.on_cancel:
            self.on_cancel()

    def _on_drag_start(self, event):
        """Surukleme basla — mouse offset kaydet."""
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag_move(self, event):
        """Pencereyi mouse ile surukle."""
        x = self.root.winfo_x() + (event.x - self._drag_x)
        y = self.root.winfo_y() + (event.y - self._drag_y)
        self.root.geometry(f"+{x}+{y}")

    def _pill(self, x1, y1, x2, y2, r=20, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def destroy(self):
        self.timer_running = False
        if self.root:
            self.root.destroy()
            self.root = None


class TranslationPopup:
    """Mouse'u takip eden ceviri popup'i."""

    def __init__(self):
        self.win = None
        self._auto_hide_id = None
        self._follow_id = None
        self._offset_x = 16
        self._offset_y = 16

    def show(self, text: str):
        """Ceviriyi mouse yaninda goster ve takip et."""
        self.hide()

        self.win = tk.Toplevel()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="#010101")
        self.win.attributes("-transparentcolor", "#010101")
        self.win.attributes("-alpha", 0.95)
        self.win.wm_attributes("-disabled", True)

        max_w = 360

        # Siyah pill frame
        frame = tk.Frame(self.win, bg="#0a0a0a", highlightbackground="#2c2c2e",
                         highlightthickness=1, bd=0)
        frame.pack(padx=3, pady=3)

        inner = tk.Frame(frame, bg="#0a0a0a")
        inner.pack(padx=14, pady=10)

        # Ceviri metni
        tk.Label(
            inner, text=text, font=("Segoe UI", 11),
            fg="#f5f5f7", bg="#0a0a0a",
            wraplength=max_w - 36, justify="left", anchor="nw",
        ).pack()

        self.win.update_idletasks()

        # Ilk pozisyon
        self._update_position()

        # Mouse'u takip et
        self._follow_mouse()


    def _update_position(self):
        """Popup'i mouse yanina tasit."""
        if not self.win:
            return
        cursor = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))

        ww = self.win.winfo_reqwidth()
        wh = self.win.winfo_reqheight()
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()

        px = cursor.x + self._offset_x
        py = cursor.y + self._offset_y

        # Ekran disina cikmasin
        if px + ww > sw - 10:
            px = cursor.x - ww - 8
        if py + wh > sh - 10:
            py = cursor.y - wh - 8
        px = max(5, px)
        py = max(5, py)

        self.win.geometry(f"+{px}+{py}")

    def _follow_mouse(self):
        """Mouse'u surekli takip et."""
        if not self.win:
            return
        self._update_position()
        self._follow_id = self.win.after(30, self._follow_mouse)

    def hide(self):
        """Popup'i kapat."""
        if self.win:
            if self._auto_hide_id:
                try:
                    self.win.after_cancel(self._auto_hide_id)
                except Exception:
                    pass
                self._auto_hide_id = None
            if self._follow_id:
                try:
                    self.win.after_cancel(self._follow_id)
                except Exception:
                    pass
                self._follow_id = None
            try:
                self.win.destroy()
            except Exception:
                pass
            self.win = None


def get_env_path():
    """env dosya yolunu dondur."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def save_api_key(api_key: str):
    """API key'i .env dosyasina kaydet."""
    with open(get_env_path(), "w", encoding="utf-8") as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")


def load_api_key() -> str:
    """Mevcut API key'i .env dosyasindan oku."""
    env_path = get_env_path()
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip()
    return ""


def mask_key(key: str) -> str:
    """API key'i maskeleyerek goster: sk-...son4"""
    if len(key) > 8:
        return f"{key[:3]}...{key[-4:]}"
    return "***"


class VoiceToTextApp:
    """Ana uygulama sinifi."""

    def __init__(self):
        # API key yoksa ayarlar penceresini ac
        if not config.OPENAI_API_KEY:
            self._show_settings_blocking()
            if not config.OPENAI_API_KEY:
                messagebox.showerror("Hata", "API anahtari girilmedi. Uygulama kapatiliyor.")
                sys.exit(1)

        self.recorder = AudioRecorder()
        self.transcriber = WhisperTranscriber()
        self.indicator = FloatingIndicator()
        self.indicator.set_recorder(self.recorder)
        self.indicator.on_cancel = self._cancel_recording
        self.translation_popup = TranslationPopup()

        self.is_recording = False
        self.current_language = None
        self.current_language_name = "Otomatik"

        # ALT double-tap state (ses kaydi)
        self.alt_press_time = 0
        self.alt_last_release_time = 0
        self.other_key_pressed = False

        # CTRL double-tap state (ceviri)
        self.ctrl_press_time = 0
        self.ctrl_last_release_time = 0
        self.ctrl_other_key_pressed = False


        # Kayit basladiginda aktif pencere
        self.recording_start_hwnd = None

        # Yapistirma oncesi clipboard'i korumak icin
        self._clipboard_backup = None

        self.keyboard_listener = None
        self.tray_icon = None

    def _set_language(self, lang_name, lang_code):
        """Dil secimini degistir."""
        self.current_language = lang_code
        self.current_language_name = lang_name

    def _make_language_callback(self, lang_name, lang_code):
        """Her dil icin callback olustur."""
        def callback(icon, item):
            self._set_language(lang_name, lang_code)
        return callback

    def _is_language_selected(self, lang_name, lang_code):
        """Dil secili mi kontrol et."""
        def check(item):
            return self.current_language == lang_code
        return check

    def _is_alt_key(self, key):
        return key == keyboard.Key.alt_l or key == keyboard.Key.alt_r

    def _is_ctrl_key(self, key):
        return key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r

    def on_key_press(self, key):
        """Tus basimi event handler."""
        try:
            if key == keyboard.Key.esc:
                if self.is_recording:
                    self._cancel_recording()
                elif self.translation_popup.win:
                    self.translation_popup.hide()
                return
            if self._is_alt_key(key):
                self.alt_press_time = time.time()
                self.other_key_pressed = False
            elif self._is_ctrl_key(key):
                self.ctrl_press_time = time.time()
                self.ctrl_other_key_pressed = False
            else:
                self.other_key_pressed = True
                self.ctrl_other_key_pressed = True
        except Exception as e:
            print(f"Key press hatasi: {e}")

    def on_key_release(self, key):
        """Tus birakma event handler — ALT double-tap + SPACE double-tap."""
        try:
            now = time.time()

            # --- CTRL double-tap → ceviri ---
            if self._is_ctrl_key(key):
                hold_ms = (now - self.ctrl_press_time) * 1000
                if hold_ms > config.MAX_TAP_HOLD_MS:
                    self.ctrl_last_release_time = 0
                    return
                if self.ctrl_other_key_pressed:
                    self.ctrl_last_release_time = 0
                    return
                gap_ms = (now - self.ctrl_last_release_time) * 1000
                if self.ctrl_last_release_time > 0 and gap_ms < config.DOUBLE_TAP_INTERVAL_MS:
                    self.ctrl_last_release_time = 0
                    self._handle_translation()
                else:
                    self.ctrl_last_release_time = now
                return

            # --- ALT double-tap → ses kaydi ---
            if not self._is_alt_key(key):
                return

            hold_ms = (now - self.alt_press_time) * 1000
            if hold_ms > config.MAX_TAP_HOLD_MS:
                self.alt_last_release_time = 0
                return

            if self.other_key_pressed:
                self.alt_last_release_time = 0
                return

            gap_ms = (now - self.alt_last_release_time) * 1000
            if self.alt_last_release_time > 0 and gap_ms < config.DOUBLE_TAP_INTERVAL_MS:
                self.alt_last_release_time = 0
                self._toggle_recording()
            else:
                self.alt_last_release_time = now
        except Exception as e:
            print(f"Key release hatasi: {e}")

    def _get_selected_text(self) -> str:
        """Secili metni al — Ctrl+C simule edip clipboard'dan oku, sonra clipboard'i restore et."""
        old_clip = ""
        try:
            old_clip = pyperclip.paste()
        except Exception:
            pass

        # Ctrl+C simule et
        ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        time.sleep(0.03)
        ctypes.windll.user32.keybd_event(0x43, 0, 0, 0)  # C down
        time.sleep(0.03)
        ctypes.windll.user32.keybd_event(0x43, 0, 0x0002, 0)  # C up
        ctypes.windll.user32.keybd_event(0x11, 0, 0x0002, 0)  # Ctrl up
        time.sleep(0.15)

        try:
            new_clip = pyperclip.paste()
        except Exception:
            return ""

        # Clipboard'i eski haline dondur
        try:
            pyperclip.copy(old_clip)
        except Exception:
            pass

        if not new_clip or new_clip == old_clip:
            return ""

        text = new_clip.strip()
        if len(text) > 2000:
            text = text[:2000]

        return text

    def _translate_text(self, text: str) -> str:
        """Metni Turkciye cevir."""
        try:
            response = self.transcriber.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a translator. Translate the given text to Turkish. Only output the translation, nothing else."},
                    {"role": "user", "content": text},
                ],
                max_tokens=1000,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Ceviri hatasi: {e}")
            return f"Ceviri hatasi: {e}"

    def _handle_translation(self):
        """Secili metni cevirip popup goster."""
        selected = self._get_selected_text()
        if not selected:
            return

        def do_translate():
            result = self._translate_text(selected)
            if self.indicator.root:
                self.indicator.root.after(0, lambda: self.translation_popup.show(result))

        threading.Thread(target=do_translate, daemon=True).start()

    def _toggle_recording(self):
        """ALT x2 — ses kaydi baslat/durdur."""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        """Kaydi baslat."""
        # Mevcut clipboard'i yedekle
        try:
            self._clipboard_backup = pyperclip.paste()
        except Exception:
            self._clipboard_backup = None
        self.recording_start_hwnd = ctypes.windll.user32.GetForegroundWindow()
        self.is_recording = True
        self.indicator.show(config.MSG_LISTENING)
        self.recorder.start_recording()

    def _cancel_recording(self):
        """Kaydi iptal et — API'ye gonderme, sessizce kapat."""
        if not self.is_recording:
            return
        self.is_recording = False
        self.recorder.stop_recording()  # Kaydi durdur ama kullanma
        self.recorder.cleanup()
        self.indicator.hide()
        print("Kayit iptal edildi.")

    def _stop_recording(self):
        """Kaydi durdur ve isle."""
        self.is_recording = False
        self.indicator.update_message(config.MSG_PROCESSING)

        audio_path = self.recorder.stop_recording()
        if not audio_path:
            self.indicator.update_message(config.MSG_RECORDING_TOO_SHORT)
            time.sleep(1)
            self.indicator.hide()
            return

        threading.Thread(target=self._process_audio, args=(audio_path,)).start()

    def _send_paste(self):
        """Windows keybd_event ile Ctrl+V simule et."""
        VK_CONTROL = 0x11
        VK_V = 0x56
        KEYEVENTF_KEYUP = 0x0002

        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(VK_V, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

    def _process_audio(self, audio_path: str):
        """Ses dosyasini isle ve sonucu yapistir."""
        try:
            text = self.transcriber.transcribe(audio_path, self.current_language)

            if text:
                pyperclip.copy(text)
                time.sleep(0.1)

                if self.recording_start_hwnd:
                    ctypes.windll.user32.SetForegroundWindow(self.recording_start_hwnd)
                    time.sleep(0.3)

                # Secimi kaldir — End tusuna basarak imleci sona tasit
                ctypes.windll.user32.keybd_event(0x23, 0, 0, 0)  # End down
                ctypes.windll.user32.keybd_event(0x23, 0, 0x0002, 0)  # End up
                time.sleep(0.05)

                self._send_paste()
                self.indicator.update_message(config.MSG_SUCCESS)
            else:
                self.indicator.update_message(config.MSG_ERROR)
        except Exception as e:
            print(f"Isleme hatasi: {e}")
            self.indicator.update_message(config.MSG_ERROR)

        time.sleep(1)
        self.indicator.hide()

    def _create_tray_icon(self) -> Image.Image:
        """System tray icin ikon olustur."""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([4, 4, size - 4, size - 4], fill='#2196F3')
        draw.rounded_rectangle([24, 12, 40, 36], radius=8, fill='white')
        draw.rectangle([30, 36, 34, 44], fill='white')
        draw.rectangle([22, 44, 42, 48], fill='white')
        draw.arc([18, 24, 46, 44], start=0, end=180, fill='white', width=3)
        return image

    def _on_tray_quit(self, icon, item):
        """Tray menusunden cikis."""
        try:
            self.stop()
        except Exception:
            pass
        try:
            icon.visible = False
            icon.stop()
        except Exception:
            pass
        os._exit(0)

    def _show_settings_blocking(self):
        """Ilk calistirmada API key giris penceresi (blocking)."""
        self._open_settings_window(blocking=True)

    def _on_tray_settings(self, icon, item):
        """Tray menusunden ayarlar penceresi ac."""
        threading.Thread(target=self._open_settings_window, daemon=True).start()

    def _open_settings_window(self, blocking=False):
        """Ayarlar penceresi."""
        BG = "#161618"
        TEXT = "#f5f5f7"
        TEXT_DIM = "#86868b"
        GREEN = "#30D158"
        GRAY_BTN = "#3a3a3c"

        win = tk.Tk() if blocking else tk.Toplevel()
        win.title("Voice to Text")
        win.configure(bg=BG)
        win.attributes("-topmost", True)

        # DPI awareness — Windows scaling sorununu coz
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        try:
            win.tk.call('tk', 'scaling', win.winfo_fpixels('1i') / 72)
        except Exception:
            pass

        # Baslik
        tk.Label(
            win, text="Ayarlar", font=("Segoe UI", 16, "bold"),
            fg=TEXT, bg=BG,
        ).pack(padx=40, pady=(30, 0), anchor="w")

        tk.Label(
            win, text="Ses tanima icin OpenAI API anahtarinizi girin.",
            font=("Segoe UI", 9), fg=TEXT_DIM, bg=BG,
        ).pack(padx=40, pady=(4, 0), anchor="w")

        # API Key label
        tk.Label(
            win, text="API Key", font=("Segoe UI Semibold", 10),
            fg=TEXT, bg=BG,
        ).pack(padx=40, pady=(24, 0), anchor="w")

        # Input
        current_key = load_api_key()
        entry = tk.Entry(
            win, font=("Consolas", 11),
            bg="#0a0a0a", fg=TEXT, insertbackground=TEXT,
            relief="solid", bd=1, highlightthickness=0,
        )
        entry.pack(padx=40, pady=(6, 0), fill="x")
        entry.insert(0, current_key)
        entry.focus_set()

        # Status
        status_label = tk.Label(
            win, text="", font=("Segoe UI", 9),
            fg=TEXT_DIM, bg=BG, anchor="w",
        )
        status_label.pack(padx=40, pady=(8, 0), fill="x")

        def on_save():
            key = entry.get().strip()
            if not key:
                status_label.config(text="API key bos olamaz.", fg="#FF3B30")
                return
            if not key.startswith("sk-"):
                status_label.config(text="Gecersiz format — sk- ile baslamali.", fg="#FF9500")
                return
            save_api_key(key)
            config.OPENAI_API_KEY = key
            status_label.config(text="Kaydedildi.", fg=GREEN)
            win.after(1000, win.destroy)

        # Butonlar
        btn_frame = tk.Frame(win, bg=BG)
        btn_frame.pack(padx=40, pady=(24, 30), fill="x")

        tk.Button(
            btn_frame, text="  Kaydet  ", command=on_save,
            font=("Segoe UI Semibold", 10), bg=GREEN, fg="#000000",
            activebackground="#28b84c", activeforeground="#000000",
            relief="flat", bd=0, padx=16, pady=8, cursor="hand2",
        ).pack(side="right")

        tk.Button(
            btn_frame, text="  Iptal  ", command=win.destroy,
            font=("Segoe UI", 10), bg=GRAY_BTN, fg=TEXT,
            activebackground="#4a4a4c", activeforeground=TEXT,
            relief="flat", bd=0, padx=16, pady=8, cursor="hand2",
        ).pack(side="right", padx=(0, 10))

        win.bind("<Return>", lambda e: on_save())
        win.bind("<Escape>", lambda e: win.destroy())

        # Pencereyi icerige gore boyutlandir, sonra ortala
        win.update_idletasks()
        win.minsize(460, win.winfo_reqheight())
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        ww = max(460, win.winfo_reqwidth())
        wh = win.winfo_reqheight()
        win.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")
        win.resizable(False, False)

        if blocking:
            win.mainloop()
        else:
            win.grab_set()
            win.wait_window()

    def _on_tray_about(self, icon, item):
        """Hakkinda penceresi."""
        messagebox.showinfo(
            "Hakkinda",
            "Voice to Text App v2.0\n\n"
            "ALT x2 ile kayit baslat/durdur.\n"
            "Ses, Whisper API ile metne donusturulur.\n\n"
            "2026"
        )

    def run(self):
        """Uygulamayi baslat."""
        print(f"{config.TRAY_TITLE} baslatiliyor...")
        print("ALT x2 ile kayit baslat/durdur")

        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()

        icon_image = self._create_tray_icon()

        language_items = []
        for lang_name, lang_code in config.SUPPORTED_LANGUAGES.items():
            language_items.append(
                pystray.MenuItem(
                    lang_name,
                    self._make_language_callback(lang_name, lang_code),
                    checked=self._is_language_selected(lang_name, lang_code)
                )
            )

        menu = pystray.Menu(
            pystray.MenuItem("Dil", pystray.Menu(*language_items)),
            pystray.MenuItem("Ayarlar", self._on_tray_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(config.MENU_ABOUT, self._on_tray_about),
            pystray.MenuItem(config.MENU_QUIT, self._on_tray_quit)
        )

        self.tray_icon = pystray.Icon(
            config.TRAY_TITLE, icon_image, config.TRAY_TOOLTIP, menu
        )

        indicator_thread = threading.Thread(target=self._run_indicator_loop, daemon=True)
        indicator_thread.start()

        self.tray_icon.run()

    def _run_indicator_loop(self):
        """Indicator icin tkinter mainloop."""
        self.indicator._create_window()
        self.indicator.root.mainloop()

    def stop(self):
        """Uygulamayi durdur."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.recorder.cleanup()
        self.indicator.destroy()


def check_single_instance():
    """Tek instance kontrolu - mutex ile."""
    mutex_name = "VoiceToTextApp_SingleInstance_Mutex"
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        return None
    return mutex


def main():
    """Ana giris noktasi."""
    mutex = check_single_instance()
    if mutex is None:
        messagebox.showinfo("Voice to Text", "Uygulama zaten calisiyor.\nSystem tray'de bulabilirsiniz.")
        sys.exit(0)

    try:
        app = VoiceToTextApp()
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Hata: {e}")
        messagebox.showerror("Hata", str(e))
        sys.exit(1)
    finally:
        if mutex:
            ctypes.windll.kernel32.ReleaseMutex(mutex)
            ctypes.windll.kernel32.CloseHandle(mutex)


if __name__ == "__main__":
    main()
