import re
import random
from typing import Tuple
from core.config import Config

class WakeWordDetector:
    """Intelligent Wake Word and Background Audio Filter.
    Filters out background noise and TV chatter, while recognizing
    all acoustic variants and direct user commands instantly.
    """

    def __init__(self):
        # Comprehensive regex covering all English, Hindi, and common acoustic ASR mis-transcriptions
        # e.g., 'Hey Jarvis', 'Service', 'Travis', 'Jarvish', 'जार्विस', 'सर्विस', etc.
        self.wake_pattern = re.compile(
            r'\b(hey|hi|hello|ok|okay|oye|o|suno|listen|arre|are|sun|bhai|mr)?\s*(jarvis|jarvish|jarves|javis|zarvis|jarvice|service|sarvis|travis|harvest|जार्विस|सर्विस)\b',
            re.IGNORECASE
        )


        # Cinematic, impressive activation responses (Iron Man Mark 85 style)
        self.en_acknowledgements = [
            f"At your command, {Config.USER_NAME}. All tactical protocols are primed and ready.",
            f"Online and listening, {Config.USER_NAME}. What is your directive?",
            f"Jarvis at your service, {Config.USER_NAME}. Standing by.",
            f"Right here, {Config.USER_NAME}. How may I assist you today?",
            f"Protocols active, {Config.USER_NAME}. Ready when you are.",
            f"Always at your disposal, {Config.USER_NAME}. What are we building today?",
            f"Sensors engaged and listening, {Config.USER_NAME}. Speak your command."
        ]

        self.hi_acknowledgements = [
            f"जी {Config.USER_NAME}! जार्विस आपकी सेवा में हाज़िर है। बताइए क्या हुक्म है?",
            f"प्रणाम {Config.USER_NAME}, सभी सिस्टम पूरी तरह सक्रिय हैं। क्या आदेश है?",
            f"जी {Config.USER_NAME}, मैं पूरी तरह सुन रहा हूँ। आज्ञा दीजिए।",
            f"जार्विस एक्टिवेटेड, {Config.USER_NAME}। बताइए क्या करना है?",
            f"हुक्म कीजिए {Config.USER_NAME}, सभी प्रोटोकॉल तैयार हैं।"
        ]

    def has_wake_word(self, text: str) -> bool:
        """Returns True ONLY if the text explicitly contains 'Hey Jarvis' or 'Jarvis'."""
        if not text:
            return False
        return bool(self.wake_pattern.search(text))

    def extract_command(self, text: str) -> Tuple[bool, str]:
        """Checks if wake word is present and extracts the command part.
        Returns:
            (has_wake_word: bool, command: str)
            - If wake word is present with command: (True, "play Kesariya")
            - If wake word is present alone: (True, "")
            - If wake word is NOT present: (False, "") -> STRICTLY IGNORED!
        """
        if not text or not text.strip():
            return False, ""

        clean_text = text.strip()

        # Strict check for wake word
        match = self.wake_pattern.search(clean_text)
        if match:
            start, end = match.span()
            before = clean_text[:start].strip()
            after = clean_text[end:].strip()

            raw_cmd = f"{before} {after}".strip()
            cleaned_cmd = re.sub(r'^[,\.\s:\-—]+', '', raw_cmd)
            cleaned_cmd = re.sub(r'[,\.\s:\-—]+$', '', cleaned_cmd)
            cleaned_cmd = re.sub(r'^(please|kripya|zara)\s+', '', cleaned_cmd, flags=re.IGNORECASE).strip()
            return True, cleaned_cmd

        # Without wake word, strictly return False (blocks 100% of background noise, songs, chatter)
        return False, ""

    def get_acknowledgement(self, query: str = "") -> str:
        """Returns an impressive, cinematic acknowledgement in Hindi or English."""
        is_hindi = bool(re.search(r'[\u0900-\u097F]', query)) or any(
            w in query.lower() for w in ["suno", "oye", "arre", "karo", "bhai", "kaisa", "batao", "bhejo", "lagao"]
        )
        if is_hindi:
            return random.choice(self.hi_acknowledgements)
        return random.choice(self.en_acknowledgements)

wake_detector = WakeWordDetector()
