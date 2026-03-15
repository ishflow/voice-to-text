<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078D6?style=flat-square&logo=windows" />
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/API-OpenAI%20Whisper-412991?style=flat-square&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
</p>

# Voice to Text

A fast, minimal voice-to-text app for Windows. Double-tap **ALT** to start recording, speak, double-tap **ALT** again — your speech is transcribed and automatically pasted wherever your cursor is.

```
  ALT ALT  -->  Speak  -->  ALT ALT  -->  Text appears
```

## Features

- **ALT x2** to start/stop recording (won't trigger Alt+Tab or other shortcuts)
- **Auto-paste** into any app — terminal, browser, editor, everywhere
- **Multi-language** support — Turkish, English, Russian (auto-detect available)
- **Minimal dark UI** — floating pill indicator with live waveform
- **System tray** — runs quietly in the background
- **Settings panel** — enter your API key from the tray menu, no config files needed
- **Smart window memory** — pastes back into the window where you started recording

## Demo

```
 [Recording]               [Processing]            [Done]
 +-----------------------+  +-----------------------+  Text is pasted
 | * ||||||||||||| 0:03  |  | * ||||||||||||| 0:03  |  automatically
 +-----------------------+  +-----------------------+  into your app
   red dot + waveform         orange dot                green dot
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run

```bash
pythonw main.py
```

### 3. Set up your API key

On first launch, a settings window will appear. Enter your [OpenAI API key](https://platform.openai.com/api-keys) and click **Save**.

You can also change it anytime: **right-click tray icon > Settings**.

## How It Works

| Step | What happens |
|------|-------------|
| **ALT x2** | Recording starts, floating indicator appears |
| **Speak** | Audio captured via microphone, waveform animates |
| **ALT x2** | Recording stops, audio sent to Whisper API |
| **Auto-paste** | Transcribed text is pasted into the active window |

The app remembers which window was active when you started recording. After transcription, it switches back to that window and pastes the text automatically.

## Configuration

Settings are in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `DOUBLE_TAP_INTERVAL_MS` | 300 | Max time between two ALT taps (ms) |
| `MAX_TAP_HOLD_MS` | 200 | Max hold time per tap — ignores long presses |
| `MAX_RECORDING_DURATION` | 600 | Maximum recording length (seconds) |
| `SAMPLE_RATE` | 16000 | Audio sample rate (16kHz optimal for Whisper) |

### Supported Languages

| Language | Code |
|----------|------|
| Auto-detect | `None` |
| Turkish | `tr` |
| English | `en` |
| Russian | `ru` |

Change language from tray menu: **right-click > Language**.

## Cost

Whisper API pricing: **~$0.006 per minute**

| Usage | Cost |
|-------|------|
| 10 min/day | ~$0.06/day |
| 1 hour/day | ~$0.36/day |

## System Requirements

- Windows 10/11
- Python 3.11+
- Microphone
- OpenAI API key

## File Structure

```
voice-to-text/
  main.py            # App (recorder, UI, hotkey, paste logic)
  config.py           # Configuration
  requirements.txt    # Python dependencies
  .env                # Your API key (created via Settings, git-ignored)
  icon.ico            # App icon
```

## Troubleshooting

**Microphone not detected**
Check Windows Sound Settings > default input device. Make sure the app has microphone permission.

**ALT x2 not working**
Make sure you tap ALT quickly (within 300ms) without pressing any other key. Long presses and Alt+Tab are ignored by design.

**Paste not working in some apps**
The app uses Windows `keybd_event` to simulate Ctrl+V. Some apps with custom input handling may not respond. In that case, the text is still on your clipboard — just press Ctrl+V manually.

## License

MIT
