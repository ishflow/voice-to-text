"""
Voice to Text App - Configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# API Configuration
# =============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Whisper API settings
WHISPER_MODEL = "whisper-1"
WHISPER_LANGUAGE = None  # Baslangicta otomatik

# Desteklenen diller (Whisper API tarafindan desteklenenler)
SUPPORTED_LANGUAGES = {
    "Otomatik": None,
    "Turkce": "tr",
    "English": "en",
    "Русский": "ru",
}
# Not: Ozbekce, Kazakca, Kirgizca Whisper API tarafindan desteklenmiyor

# =============================================================================
# Hotkey Configuration
# =============================================================================
# Double-tap ALT to toggle recording
DOUBLE_TAP_KEY = "alt"
DOUBLE_TAP_INTERVAL_MS = 300  # Max time between two taps (ms)
MAX_TAP_HOLD_MS = 200  # Max hold time per tap (ignore long presses)

# =============================================================================
# Audio Recording Configuration
# =============================================================================
# Sample rate (16kHz is optimal for Whisper)
SAMPLE_RATE = 16000

# Audio format settings
CHANNELS = 1  # Mono
CHUNK_SIZE = 1024

# Maximum recording duration (seconds)
MAX_RECORDING_DURATION = 600  # 10 dakika

# Temporary audio file path
import tempfile
TEMP_AUDIO_FILE = os.path.join(tempfile.gettempdir(), "voice_to_text_recording.wav")

# =============================================================================
# UI Configuration
# =============================================================================
# Floating indicator settings
INDICATOR_WIDTH = 150
INDICATOR_HEIGHT = 40
INDICATOR_BG_COLOR = "#2196F3"  # Blue
INDICATOR_TEXT_COLOR = "#FFFFFF"  # White
INDICATOR_FONT = ("Segoe UI", 12, "bold")

# Indicator position offset from top-right corner
INDICATOR_OFFSET_X = 20
INDICATOR_OFFSET_Y = 20

# =============================================================================
# Messages
# =============================================================================
MSG_LISTENING = "Dinliyor"
MSG_PROCESSING = "Isleniyor..."
MSG_SUCCESS = "Tamam"
MSG_ERROR = "Hata"
MSG_NO_API_KEY = "API anahtari bulunamadi! .env dosyasini kontrol edin."
MSG_RECORDING_TOO_SHORT = "Cok kisa"

# System tray messages
TRAY_TITLE = "Voice to Text"
TRAY_TOOLTIP = "ALT x2 ile kayit baslatin"
MENU_QUIT = "Cikis"
MENU_ABOUT = "Hakkinda"
