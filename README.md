# ⚡ J.A.R.V.I.S. // Stark Industries Tactical OS (macOS Edition)

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://python.org)
[![macOS](https://img.shields.io/badge/macOS-Apple%20Silicon%20%7C%20Intel-000000?logo=apple&logoColor=white)](https://apple.com)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini%20Flash-4285F4?logo=google&logoColor=white)](https://aistudio.google.com)
[![UI](https://img.shields.io/badge/HUD-Holographic%20Canvas%20GUI-00f0ff)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An ultra-advanced, intelligent desktop AI voice assistant built natively for **macOS (Apple Silicon & Intel)**. Powered by a **Dual-Engine Brain (Google Gemini Flash with Real-Time Function Calling + Offline Multi-Lingual NLP)** and presented with a futuristic **Iron Man Mark 85 Holographic Tactical HUD**.

---

```
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
    [ STARK INDUSTRIES - MARK 85 AI ASSISTANT ]
```

---

## 🌟 Key Features

### 🖥️ 1. Holographic Graphical HUD Interface
- **Dynamic Arc Reactor Canvas**: Real-time 60fps mechanical core animation with rotating concentric rings, energy coils, and state-reactive particle pulses.
- **Live Audio Waveform Visualizer**: Smooth sound equalizer oscillating in real-time as you speak or Jarvis responds.
- **Hardware Telemetry HUD**: Live gauges for **CPU Utilization**, **Memory (RAM)**, **Battery Percentage & Charging State**, and **SSD Free Storage**.
- **Interactive Command Deck**: One-click quick actions (*Play YouTube Hits, Screenshot, Weather, Volume, Lock Screen, Diagnostics*) plus manual Mic activation button.

### 🛡️ 2. Wake Word Shield & Background Noise Filter
- **Zero Accidental Triggers**: Automatically filters out and ignores background songs, music on speakers, room chatter, and television noise.
- **Instant Activation**: Jarvis **only** triggers when you say **"Hey Jarvis"**, **"Jarvis"**, or **"जार्विस"**.
- **Inline Command Execution**: Say *"Hey Jarvis play Kesariya on YouTube"* and it executes immediately without waiting.

### 🗣️ 3. Deep Male Voice Output (Stark British & Deep Hindi)
- **Hindi Voice**: Deep masculine baritone using Microsoft Neural `hi-IN-MadhurNeural` tuned with **`-8Hz` pitch** (with macOS native male voice `Rishi` as offline fallback).
- **English Voice**: Sleek British Jarvis voice (`en-GB-RyanNeural` or macOS `Daniel`).

### 🧠 4. Dual-Engine Intelligence Core
- **Online (Gemini Flash AI)**: Fast multi-modal LLM with automated tool execution (opens applications, adjusts hardware volume, manages media, checks weather, captures screens).
- **Offline (High-Speed NLP Intent Engine)**: Seamless offline operation for core macOS commands in **English, Hindi, and Hinglish**.

### 💻 5. Complete macOS Automations & Tools
- 🎵 **Direct YouTube Auto-Play**: Extracts video ID and opens the video for immediate autoplay.
- 🚀 **App Launcher**: Open and close any macOS app (*Chrome, Brave, Safari, Spotify, VS Code, Notes, Calculator, etc.*).
- 📸 **Silent Screen Capture**: Instant screenshot saved with timestamp to `screenshots/`.
- 🔊 **System Audio Control**: Set volume %, increase/decrease, mute/unmute.
- 🔋 **Battery & Diagnostics**: Instant battery state, CPU/RAM telemetry.
- 🔒 **Security**: Fast Mac screen lock.
- ⛅ **Live Weather**: Real-time weather for any city worldwide.
- 📝 **Smart Notes**: Dictate and review quick notes saved in `notes/`.

---

## 🚀 Quick Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/Jarvis.git
cd Jarvis
```

### 2. Configure Environment (`.env`)
Copy the example environment template:
```bash
cp .env.example .env
```
Open `.env` and add your **free Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com)):
```ini
GEMINI_API_KEY="your_api_key_here"
```

### 3. Run Jarvis
Simply execute the launch script (it will automatically create the virtual environment and install dependencies on first run):
```bash
./run.sh
```
*Jarvis will initialize the Mark 85 OS and open the Holographic Tactical UI window automatically!*

---

## 🎯 Command Modes

| Launch Command | Mode Description |
|---|---|
| `./run.sh` | **Holographic Graphical HUD UI** (Default desktop window mode) |
| `./run.sh --ui` | Explicitly launch the Tactical GUI window |
| `./run.sh --voice` | Terminal Voice Mode with Iron Man boot animation & live wave |
| `./run.sh --text` | Terminal Keyboard Input Mode (ideal for silent environments) |
| `./run.sh --test` | Runs full system diagnostic self-test (Sensors, AI, Battery, Audio) |

---

## 🎙️ Example Voice Commands

| Category | Spoken Command | What Jarvis Does |
|---|---|---|
| 🎵 **Music** | *"Hey Jarvis, play Bohemian Rhapsody"* | Searches YouTube and autoplays immediately |
| 🎵 **Hindi Music** | *"Jarvis, Arijit Singh ke gaane chalao"* | Autoplays Arijit Singh hits on YouTube |
| 📸 **Screenshot** | *"Hey Jarvis, take a screenshot"* | Saves Mac display to `screenshots/` |
| 🔊 **Audio** | *"Jarvis, volume 70"* / *"Volume badhao"* | Adjusts macOS system audio slider |
| 🔋 **Battery** | *"Hey Jarvis, battery status"* / *"Battery kitni hai"* | Reports percentage & charging state |
| ⛅ **Weather** | *"Hey Jarvis, what's the weather in Mumbai?"* | Reports live temperature, humidity, and wind |
| 🚀 **Apps** | *"Jarvis, open Spotify"* / *"Close Safari"* | Launches or quits macOS applications |
| 🔒 **Security** | *"Hey Jarvis, lock screen"* | Instantly locks your Mac |
| 🧠 **Chat** | *"Jarvis, how are you today?"* / *"Kaise ho?"* | Responds in sleek, witty tone |

---

## 📂 Project Architecture

```
Jarvis/
├── jarvis.py              # Main application entry point & CLI controller
├── run.sh                 # One-click launcher script
├── requirements.txt       # Python package dependencies
├── .env.example           # Environment configuration template
├── .gitignore             # Git ignore file protecting API keys & personal data
├── LICENSE                # MIT Open Source License
├── core/
│   ├── brain.py           # Gemini LLM + Offline Multi-Lingual NLP Engine
│   ├── config.py          # Centralized environment loader
│   ├── listener.py        # Clamped acoustic speech recognition engine
│   ├── speaker.py         # Dual TTS engine (Neural Edge + macOS say)
│   ├── tools.py           # macOS automations (App, YouTube, Audio, Screen)
│   └── wakeword.py        # Wake word detector & background audio filter
├── ui/
│   ├── hud.py             # Rich terminal Arc Reactor animation & tables
│   ├── server.py          # Asynchronous aiohttp server & browser window launcher
│   └── web/
│       ├── index.html     # Mark 85 Holographic HUD structure
│       ├── style.css      # Cyberpunk Stark metallic styling & animations
│       └── app.js         # Canvas Arc Reactor & live audio visualizer
├── notes/                 # Storage for user dictated notes (.gitkeep)
└── screenshots/           # Storage for captured screenshots (.gitkeep)
```

---

## 🛡️ Security & Privacy
- **Zero API Key Leakage**: `.env` is ignored by `.gitignore` so your private API keys are never pushed to GitHub.
- **Local macOS Controls**: All scripts use local AppleScripts and native macOS binaries (`screencapture`, `osascript`).
- **Background Privacy**: Speech audio is strictly processed for the wake word; stray noise and conversations are discarded immediately.

---

## 📜 License
Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more details.
