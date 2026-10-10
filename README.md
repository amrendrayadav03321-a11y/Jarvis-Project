# ⚡ J.A.R.V.I.S. // Stark Industries Tactical OS (Cross-Platform Edition)

> 🚀 **Design and built by Satyaa Yadav**

[![Author](https://img.shields.io/badge/Design%20%26%20Built%20By-Satyaa%20Yadav-ff0055?style=for-the-badge&logo=github)](https://github.com/amrendrayadav03321-a11y/Jarvis-Project)
[![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4?logo=windows&logoColor=white)](https://microsoft.com)
[![macOS](https://img.shields.io/badge/macOS-Apple%20Silicon%20%7C%20Intel-000000?logo=apple&logoColor=white)](https://apple.com)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://python.org)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini%20Flash-4285F4?logo=google&logoColor=white)](https://aistudio.google.com)
[![UI](https://img.shields.io/badge/HUD-Holographic%20Canvas%20GUI-00f0ff)](https://github.com/amrendrayadav03321-a11y/Jarvis-Project)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An ultra-advanced, intelligent desktop AI voice assistant built natively for **Windows 10/11 & macOS (Apple Silicon & Intel)**. Powered by a **Dual-Engine Brain (Google Gemini Flash with Real-Time Function Calling + Offline Multi-Lingual NLP)** and presented with a futuristic **Iron Man Mark 85 Holographic Tactical HUD**.

---

```
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
    [ STARK INDUSTRIES - MARK 85 AI ASSISTANT ]
    [ DESIGN AND BUILT BY SATYAA YADAV ]
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

### 💻 5. Complete Cross-Platform Automations & Tools (Windows 10/11 & macOS)
- 🎵 **Direct YouTube Auto-Play**: Extracts video ID and opens the video for immediate autoplay.
- 🚀 **App Launcher**: Open and close any app (*Chrome, Brave, Edge, Spotify, VS Code, Notepad/Notes, Calculator, etc.*).
- 📸 **Silent Screen Capture**: Cross-platform instant screenshot saved with timestamp to `screenshots/`.
- 🔊 **System Audio Control**: Set volume %, increase/decrease, mute/unmute via native PowerShell on Windows and AppleScript on macOS.
- 🔋 **Battery & Diagnostics**: Instant battery state (laptops) and AC power detection (desktop PCs), CPU/RAM telemetry.
- 🔒 **Security**: Fast desktop screen lock (`LockWorkStation` on Windows / `displaysleepnow` on macOS).
- ⛅ **Live Weather**: Real-time weather for any city worldwide.
- 📝 **Smart Notes**: Dictate and review quick notes saved in `notes/`.
- 📞 **Phone & WhatsApp Integration**: Open WhatsApp chats or trigger phone calls directly from contacts.

---

## 🚀 Quick Setup & Installation

> [!TIP]
> **Recommended Python for Windows:** **Python 3.12** (Standard Stable Release).  
> If your system has Python 3.14 (experimental pre-release), Windows audio drivers (`PyAudio`) will require C++ Build Tools. You can install Python 3.12 in 10 seconds via PowerShell:
> ```powershell
> winget install Python.Python.3.12
> ```

### 1. Download the Project

#### 🌟 Method A: Download ZIP (Recommended for Windows — No Git Required!)
1. Click the green **Code** button at the top right of this page and click **[Download ZIP](https://github.com/amrendrayadav03321-a11y/Jarvis-Project/archive/refs/heads/main.zip)**.
2. Extract the downloaded `Jarvis-Project-main.zip` on your computer.
3. Open the extracted folder.

#### ⚡ Method B: Windows PowerShell One-Liner (No Git Needed)
Open PowerShell and run:
```powershell
Invoke-WebRequest -Uri "https://github.com/amrendrayadav03321-a11y/Jarvis-Project/archive/refs/heads/main.zip" -OutFile "Jarvis.zip"; Expand-Archive -Path "Jarvis.zip" -DestinationPath "."; cd "Jarvis-Project-main"
```

#### 🛠️ Method C: Git Clone
If you have Git installed:
```bash
git clone https://github.com/amrendrayadav03321-a11y/Jarvis-Project.git
cd Jarvis-Project
```
> **Note for Windows:** If you see `'git' is not recognized as a cmdlet`, it means Git is not installed on your system. Either use **Method A (Download ZIP)** above, or install Git quickly in PowerShell with:
> ```powershell
> winget install --id Git.Git -e --source winget
> ```

### 2. Configure Environment (`.env`)
Copy the example environment template:
```bash
# On macOS / Linux:
cp .env.example .env

# On Windows (Command Prompt / PowerShell):
copy .env.example .env
```
Open `.env` and add your **free Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com)):
```ini
GEMINI_API_KEY="your_api_key_here"
```

### 3. Run Jarvis (1-Click Launch)

#### On Windows (10 / 11):
Simply double-click `run.bat` or run in Command Prompt / PowerShell:
```cmd
run.bat
```

#### On macOS & Linux:
Make the script executable and run:
```bash
chmod +x run.sh
./run.sh
```
*Jarvis will automatically create the virtual environment, install all dependencies, initialize the Mark 85 OS, and open the Holographic Tactical UI window!*

---

## 🎯 Command Modes

| Windows Command | macOS / Linux Command | Mode Description |
|---|---|---|
| `run.bat` | `./run.sh` | **Holographic Graphical HUD UI** (Default desktop window mode) |
| `run.bat --ui` | `./run.sh --ui` | Explicitly launch the Tactical GUI window |
| `run.bat --voice` | `./run.sh --voice` | Terminal Voice Mode with Iron Man boot animation & live wave |
| `run.bat --text` | `./run.sh --text` | Terminal Keyboard Input Mode (ideal for silent environments) |
| `run.bat --test` | `./run.sh --test` | Runs full system diagnostic self-test (Sensors, AI, Battery, Audio) |

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
├── run.bat                # 1-Click launcher script for Windows (10/11)
├── run.sh                 # 1-Click launcher script for macOS and Linux
├── requirements.txt       # Python package dependencies (Pillow, edge-tts, rich, etc.)
├── .env.example           # Environment configuration template
├── .gitignore             # Git ignore file protecting API keys & personal data
├── LICENSE                # MIT Open Source License
├── core/
│   ├── brain.py           # Gemini LLM + Offline Multi-Lingual NLP Engine
│   ├── config.py          # Centralized environment loader
│   ├── contacts.py        # Contacts directory & WhatsApp/Call launcher
│   ├── listener.py        # Cross-platform acoustic speech recognition engine
│   ├── speaker.py         # Dual TTS engine (Neural Edge + Windows SAPI / macOS say)
│   ├── tools.py           # Cross-platform automations (Windows & macOS native actions)
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
- **Native OS Automations**: Clean OS controls using native Windows PowerShell / WScript commands and native macOS AppleScript without third-party keyloggers.
- **Background Privacy**: Speech audio is strictly processed for the wake word; stray noise and ambient chatter are filtered and discarded.

---

## 👨‍💻 Author & Creator

> 🚀 **Design and built by Satyaa Yadav**
- **Creator**: **Satyaa Yadav**
- **Repository**: [amrendrayadav03321-a11y/Jarvis-Project](https://github.com/amrendrayadav03321-a11y/Jarvis-Project)
- **Architecture**: Cross-Platform AI Voice Assistant with Dual-Engine Intelligence & Stark HUD

---

## 📜 License
Distributed under the **MIT License**. Copyright (c) 2026 **Satyaa Yadav**. See [`LICENSE`](LICENSE) for more details.
