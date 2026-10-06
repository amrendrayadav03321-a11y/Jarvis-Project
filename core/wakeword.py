import re
import random
from typing import Tuple
from core.config import Config

class WakeWordDetector:
    """Intelligent Wake Word and Background Audio Filter.
    Filters out background noise, TV chatter, and background music
    unless an explicit activation trigger like 'Hey Jarvis' or 'Jarvis' is detected.
    """

    def __init__(self):
        # Comprehensive regex covering all English, Hindi, and transliterated wake phrases,
        # including common speech recognition acoustic variants (jarvish, javis, etc.)
        self.wake_pattern = re.compile(
            r'\b(hey|hi|hello|ok|okay|oye|o|suno|listen|arre|are|sun)?\s*(jarvis|jarvish|jarves|javis|zarvis|jarvice|जार्विस)\b',
            re.IGNORECASE
        )

        self.en_acknowledgements = [
            "Yes, sir?",
            "At your service, sir.",
            "Yes, I am listening.",
            "Online and ready, sir.",
            "How may I assist you, sir?"
        ]

        self.hi_acknowledgements = [
            "जी सर, बताइए?",
            "हाँ सर, मैं सुन रहा हूँ।",
            "जी सर, क्या हुक्म है?",
            "सभी सिस्टम तैयार हैं, आज्ञा दीजिए।"
        ]

    def has_wake_word(self, text: str) -> bool:
        """Returns True if the text contains any wake word variant."""
        if not text:
            return False
        return bool(self.wake_pattern.search(text))

    def extract_command(self, text: str) -> Tuple[bool, str]:
        """Checks if wake word is present and extracts the command part.
        Returns:
            (has_wake_word: bool, command: str)
            - If wake word is present and followed/preceded by a command: (True, "play music")
            - If wake word is present alone: (True, "")
            - If wake word is not present: (False, "")
        """
        if not text or not text.strip():
            return False, ""

        match = self.wake_pattern.search(text)
        if not match:
            return False, ""

        start, end = match.span()
        before = text[:start].strip()
        after = text[end:].strip()

        raw_cmd = f"{before} {after}".strip()
        # Clean leading and trailing punctuation
        cleaned_cmd = re.sub(r'^[,\.\s:\-—]+', '', raw_cmd)
        cleaned_cmd = re.sub(r'[,\.\s:\-—]+$', '', cleaned_cmd)

        # Strip courtesy fillers
        cleaned_cmd = re.sub(r'^(please|kripya|zara)\s+', '', cleaned_cmd, flags=re.IGNORECASE).strip()

        return True, cleaned_cmd

    def get_acknowledgement(self, query: str = "") -> str:
        """Returns a polite, natural acknowledgement in Hindi or English."""
        is_hindi = bool(re.search(r'[\u0900-\u097F]', query)) or any(
            w in query.lower() for w in ["suno", "oye", "arre", "karo", "bhai", "kaisa", "batao"]
        )
        if is_hindi:
            return random.choice(self.hi_acknowledgements)
        return random.choice(self.en_acknowledgements)

wake_detector = WakeWordDetector()
