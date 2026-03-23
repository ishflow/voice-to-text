<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078D6?style=flat-square&logo=windows" />
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/API-OpenAI-412991?style=flat-square&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
</p>

# Voice to Text + Instant Translate

A fast, minimal productivity tool for Windows with two powers:

**Voice to Text** — Double-tap **ALT**, speak, double-tap **ALT** again. Your speech is transcribed and auto-pasted wherever your cursor is.

**Instant Translate** — Select any text, double-tap **CTRL**. A floating popup appears next to your mouse with the Turkish translation.

**Translate to English** — Select any text, hold **CTRL+ALT**. The selected text is translated to English and replaces the original.

```
  Voice:      ALT ALT  →  Speak  →  ALT ALT  →  Text pasted
  Translate:  Select text  →  CTRL CTRL  →  Translation popup (Turkish)
  English:    Select text  →  CTRL+ALT   →  Text replaced with English translation
```

## Features

### Voice to Text
- **ALT x2** to start/stop recording (won't trigger Alt+Tab)
- **Auto-paste** into any app — terminal, browser, editor, everywhere
- **Smart window memory** — returns to the window where you started recording
- **Cancel anytime** — press **ESC** or click the **X** button on the indicator
- **Draggable indicator** — click and drag to reposition the recording pill
- **Multi-language** — Turkish, English, Russian, or auto-detect

### Instant Translate
- **CTRL x2** to translate selected text to Turkish
- **CTRL+ALT** to translate selected text to English (replaces in-place)
- **Follows your mouse** — popup moves with your cursor
- Works everywhere — browser, Slack, Notepad, any app
- Press **ESC** to dismiss

### General
- **Minimal dark UI** — floating pill with live waveform animation
- **System tray** — runs quietly in the background
- **Settings panel** — enter your API key from the tray menu
- **Status indicators** — red (recording), orange (processing), green (done)

## Quick Start

### Option A: One-click setup (recommended)

```bash
git clone https://github.com/ishflow/voice-to-text.git
cd voice-to-text
setup.bat
```

This creates a virtual environment, installs all dependencies, and prepares the `.env` file. Then run:

```bash
start.bat
```

### Option B: Manual setup

```bash
pip install -r requirements.txt
pythonw main.py
```

### Set up your API key

On first launch, a settings window appears. Enter your [OpenAI API key](https://platform.openai.com/api-keys) and click **Save**.

Change it anytime: **right-click tray icon > Settings**.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **ALT x2** | Start/stop voice recording |
| **CTRL x2** | Translate selected text to Turkish |
| **CTRL+ALT** | Translate selected text to English |
| **ESC** | Cancel recording / close translation popup |

## How Voice to Text Works

| Step | What happens |
|------|-------------|
| **ALT x2** | Recording starts, floating indicator appears |
| **Speak** | Audio captured, waveform animates in real-time |
| **ALT x2** | Recording stops, sent to Whisper API |
| **Auto-paste** | Text pasted into the window where you started |

## How Instant Translate Works

| Step | What happens |
|------|-------------|
| **Select text** | Highlight any text in any app |
| **CTRL x2** | Selected text is captured and sent to GPT-4o-mini |
| **Popup** | Turkish translation appears next to your mouse |
| **ESC** | Dismiss the popup |

## How English Translation Works

| Step | What happens |
|------|-------------|
| **Select text** | Highlight any text in any app |
| **CTRL+ALT** | Selected text is sent to GPT-4o-mini for English translation |
| **Auto-replace** | Original text is replaced with the English translation |

## Configuration

Settings are in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `DOUBLE_TAP_INTERVAL_MS` | 300 | Max time between two taps (ms) |
| `MAX_TAP_HOLD_MS` | 200 | Max hold time per tap — ignores long presses |
| `MAX_RECORDING_DURATION` | 600 | Maximum recording length (seconds) |
| `SAMPLE_RATE` | 16000 | Audio sample rate (16kHz optimal for Whisper) |

### Supported Languages (Voice)

| Language | Code |
|----------|------|
| Auto-detect | `None` |
| Turkish | `tr` |
| English | `en` |
| Russian | `ru` |

Change voice language: **right-click tray icon > Language**.

## Cost

| Feature | Model | Pricing |
|---------|-------|---------|
| Voice to Text | Whisper | ~$0.006/min |
| Translate (TR) | GPT-4o-mini | ~$0.00015/request |
| Translate (EN) | GPT-4o-mini | ~$0.00015/request |

Both features are very affordable for daily use.

## System Requirements

- Windows 10/11
- Python 3.11+
- Microphone (for voice)
- OpenAI API key

## File Structure

```
voice-to-text/
  main.py            # App (recorder, translator, UI, hotkeys)
  config.py          # Configuration
  requirements.txt   # Python dependencies
  setup.bat          # One-click setup (venv + deps)
  start.bat          # Launch the app
  .env               # Your API key (created via Settings, git-ignored)
  icon.ico           # App icon
```

## Troubleshooting

**Microphone not detected**
Check Windows Sound Settings > default input device. Make sure the app has microphone permission.

**ALT x2 / CTRL x2 not working**
Tap quickly (within 300ms) without pressing any other key between taps. Long presses and combo keys (Alt+Tab, Ctrl+C) are ignored by design.

**Paste not working in some apps**
The app uses Windows `keybd_event` to simulate Ctrl+V. If an app doesn't respond, the text is still on your clipboard — press Ctrl+V manually.

**Translation popup not appearing**
Make sure you have text selected before pressing CTRL x2. The app copies the selection via Ctrl+C internally.

## Version History

| Version | Features |
|---------|----------|
| **v2.1** | + English translation (CTRL+ALT combo), in-place text replacement |
| **v2.0** | + Instant Translate (CTRL x2), cancel button, ESC to cancel, draggable indicator |
| **v1.0** | Voice to Text with ALT x2, auto-paste, settings panel |

To switch to v1.0: `git checkout v1.0`

## License

MIT
