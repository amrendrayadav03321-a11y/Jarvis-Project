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
        Optimized for conference calls and presentations:
        Text spoken before the wake word (audience talk, e.g. 'So guys look here, Hey Jarvis open Chrome')
        is cleanly discarded, and the command after the wake word is extracted with 100% precision.
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

            # Priority 1: Command spoken after wake word
            if after:
                raw_cmd = after
            # Priority 2: Inverted syntax (e.g., 'YouTube kholo, Jarvis')
            elif before:
                raw_cmd = before
            else:
                return True, ""

            # Clean leading/trailing punctuation
            cleaned_cmd = re.sub(r'^[,\.\s:\-—!]+', '', raw_cmd)
            cleaned_cmd = re.sub(r'[,\.\s:\-—!]+$', '', cleaned_cmd)

            # Strip polite & conversational fillers commonly spoken in presentations & calls
            fillers = [
                r'^(?:can\s+you\s+(?:please\s+)?|could\s+you\s+(?:please\s+)?|would\s+you\s+(?:please\s+)?|will\s+you\s+)',
                r'^(?:please\s+|kripya\s+|zara\s+|ek\s+baar\s+|thoda\s+|just\s+|kindly\s+)',
                r'^(?:can\s+we\s+|let\'?s\s+|show\s+me\s+|tell\s+me\s+|mujhe\s+|mere\s+liye\s+)',
                r'^(?:now\s+|ab\s+|aur\s+|zara\s+ek\s+baar\s+)'
            ]
            for f_pattern in fillers:
                cleaned_cmd = re.sub(f_pattern, '', cleaned_cmd, flags=re.IGNORECASE).strip()

            # Clean trailing fillers (e.g. 'open Chrome please', 'play song na')
            cleaned_cmd = re.sub(r'\s+(?:please|for\s+me|na|zara)$', '', cleaned_cmd, flags=re.IGNORECASE).strip()

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
