import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
NOTES_DIR = BASE_DIR / "notes"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

NOTES_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Load .env file
load_dotenv(BASE_DIR / ".env")

class Config:
    # Assistant & User Identity
    ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Jarvis")
    USER_NAME = os.getenv("USER_NAME", "Sir")
    
    # AI Engine
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    
    # Audio / TTS Settings (Deep Male Voices)
    TTS_ENGINE = os.getenv("TTS_ENGINE", "edge")
    MACOS_VOICE = os.getenv("MACOS_VOICE", "Daniel")
    MACOS_HINDI_VOICE = os.getenv("MACOS_HINDI_VOICE", "Rishi")
    MACOS_HINGLISH_VOICE = os.getenv("MACOS_HINGLISH_VOICE", "Rishi")
    MACOS_RATE = int(os.getenv("MACOS_RATE", "150"))
    
    EDGE_VOICE = os.getenv("EDGE_VOICE", "en-GB-RyanNeural")
    EDGE_HINDI_VOICE = os.getenv("EDGE_HINDI_VOICE", "hi-IN-MadhurNeural")
    EDGE_PITCH = os.getenv("EDGE_PITCH", "-8Hz")
    EDGE_RATE = os.getenv("EDGE_RATE", "-2%")
    
    # Wake Word & Noise Filtering
    WAKE_WORD_REQUIRED = os.getenv("WAKE_WORD_REQUIRED", "true").lower() in ["true", "1", "yes"]
    WAKE_WORDS = os.getenv("WAKE_WORDS", "jarvis,hey jarvis,hi jarvis,hello jarvis,oye jarvis,suno jarvis,arre jarvis,जार्विस")
    
    # Microphone & Acoustic Settings
    SPEECH_LANG = os.getenv("SPEECH_LANG", "en-IN")
    MIC_DEVICE_INDEX = os.getenv("MIC_DEVICE_INDEX", "")  # Empty for auto-detection
    MIC_ENERGY_THRESHOLD = int(os.getenv("MIC_ENERGY_THRESHOLD", "150"))
    MIC_TIMEOUT = int(os.getenv("MIC_TIMEOUT", "8"))
    MIC_PHRASE_LIMIT = int(os.getenv("MIC_PHRASE_LIMIT", "12"))
    AUDIO_CHIMES = os.getenv("AUDIO_CHIMES", "true").lower() in ["true", "1", "yes"]
    
    # UI / Animation
    SHOW_BOOT_ANIMATION = os.getenv("SHOW_BOOT_ANIMATION", "true").lower() in ["true", "1", "yes"]
    
    # Weather default city
    DEFAULT_CITY = os.getenv("DEFAULT_CITY", "New Delhi")
