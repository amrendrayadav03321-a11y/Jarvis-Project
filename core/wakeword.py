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

        # Direct imperative command triggers (instantly bypass wake word check to prevent dropping intentional user commands)
        self.direct_command_pattern = re.compile(
            r'(\b(call|phone|dial|text|message|sms|whatsapp|play|open|launch|close|quit|mute|unmute|volume|sound|awaaz|screenshot|lock|sleep|restart|shutdown|weather|mausam|time|date|battery|brightness|dark mode|trash|joke|chutkula|calculate|search|google|kholo|chalao|bajao|lagao|bhejo|batao|sunao|badhao|kam karo|band karo|kheencho|nikalo|padho|likho)\b|'
            r'(खोल|चला|बजा|लगा|भेज|बता|सुना|बढ़ा|कम|बंद|लॉक|स्क्रीनशॉट|कॉल|मैसेज|गाना|मौसम|समय|हिसाब|कैलकुलेट|लिखो))',
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
        """Returns True if the text contains any wake word variant or direct command."""
        if not text:
            return False
        return bool(self.wake_pattern.search(text) or self.direct_command_pattern.search(text.strip()))

    def extract_command(self, text: str) -> Tuple[bool, str]:
        """Checks if wake word is present and extracts the command part.
        Returns:
            (has_wake_word: bool, command: str)
            - If wake word is present and followed/preceded by a command: (True, "call papa")
            - If direct command is detected without wake word: (True, "call papa")
            - If wake word is present alone: (True, "")
            - If wake word is not present: (False, "")
        """
        if not text or not text.strip():
            return False, ""

        clean_text = text.strip()

        # 1. Check for wake word
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

        # 2. Check for direct imperative command bypass (zero dropped commands)
        if self.direct_command_pattern.search(clean_text):
            return True, clean_text

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
