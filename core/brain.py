import os
import re
from typing import Optional
from core.config import Config
from core.tools import tools

class AssistantBrain:
    """Intelligent brain for Jarvis Assistant.
    Supports Google Gemini LLM with automated function calling,
    and falls back to an advanced multi-lingual NLP intent engine offline.
    """

    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        self.chat_session = None
        self.is_gemini_active = False
        self.active_model = "None"
        
        self._init_gemini()

    def _init_gemini(self):
        """Initializes Gemini AI client if API key is present."""
        if not self.api_key:
            self.is_gemini_active = False
            return
            
        try:
            from google import genai
            from google.genai import types
            
            self.client = genai.Client(api_key=self.api_key)
            
            tool_list = [
                tools.open_application,
                tools.close_application,
                tools.open_website,
                tools.search_google,
                tools.play_youtube,
                tools.control_media,
                tools.search_wikipedia,
                tools.take_screenshot,
                tools.set_volume,
                tools.adjust_volume,
                tools.mute_volume,
                tools.lock_screen,
                tools.empty_trash,
                tools.get_battery_status,
                tools.get_system_stats,
                tools.get_time_and_date,
                tools.get_weather,
                tools.create_note,
                tools.read_notes,
                tools.list_notes,
                tools.tell_joke,
                tools.execute_terminal_command
            ]
            
            system_instruction = (
                f"You are {Config.ASSISTANT_NAME}, Tony Stark's personal high-tech AI voice assistant running locally on macOS. "
                f"You address the user as {Config.USER_NAME}. "
                "You are loyal, brilliant, witty, concise, and ultra-capable.\n\n"
                "CRITICAL INSTRUCTIONS:\n"
                "1. LANGUAGE MATCHING:\n"
                "   - If the user speaks in Hindi or Hinglish (e.g. 'gaana chalao', 'kaisa chal raha hai', 'Spotify khol do', 'aaj mausam kaisa hai', 'battery batao'), "
                "     you MUST respond in fluent, respectful, natural Hindi or Hinglish (e.g. 'जी सर, अभी प्ले कर रहा हूँ।', 'सर, आज मौसम साफ है।', 'जी सर, खोल दिया है।').\n"
                "   - If the user speaks in English, respond in sleek British Jarvis English.\n\n"
                "2. IMMEDIATE ACTION-FIRST EXECUTION:\n"
                "   - When the user asks to do ANY task (play a song, open an application, adjust volume, take a screenshot, lock screen, check battery, check weather), "
                "     DO NOT give lengthy disclaimers or talk about it—IMMEDIATELY CALL THE TOOL.\n"
                "   - For music requests, pass the exact song or artist to 'play_youtube' so it plays immediately.\n"
                "   - Keep spoken answers brief (1 or 2 crisp sentences) so they are fast and conversational over voice."
            )
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=tool_list,
                temperature=0.7
            )
            
            models_to_try = [Config.GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]
            seen = set()
            for m in models_to_try:
                if not m or m in seen:
                    continue
                seen.add(m)
                try:
                    self.chat_session = self.client.chats.create(
                        model=m,
                        config=config
                    )
                    self.active_model = m
                    self.is_gemini_active = True
                    break
                except Exception:
                    continue
        except Exception:
            self.is_gemini_active = False
            self.chat_session = None

    def process(self, query: str) -> str:
        """Processes user input using Gemini LLM if active, otherwise uses smart NLP intent engine."""
        if not query or not query.strip():
            return ""

        query_clean = query.strip()

        # If Gemini is active and healthy, send to Gemini
        if self.is_gemini_active and self.chat_session:
            try:
                response = self.chat_session.send_message(query_clean)
                if response and response.text:
                    return response.text.strip()
            except Exception:
                pass

        # Offline Advanced NLP Intent Engine
        return self._process_offline_intent(query_clean)

    def _process_offline_intent(self, raw_query: str) -> str:
        """High-accuracy multi-lingual intent matching for voice commands in English & Hinglish."""
        q = raw_query.lower().strip()
        is_hindi_prompt = bool(re.search(r'[\u0900-\u097F]', raw_query)) or any(
            w in q for w in ["karo", "kholo", "chalao", "sunao", "batao", "kaise", "kya", "kitni", "hai", "likho", "saaf", "gaana", "roko", "kisne"]
        )
        
        # 0. Creator / Developer queries
        if re.search(
            r'(\b(who\s+(developed|devloped|created|made|built|programmed|coded|invented)\s+you|'
            r'who\s+is\s+your\s+(creator|developer|devloper|maker|boss|owner|father|master)|'
            r'who\s+made\s+this|'
            r'tumhe\s+kisne\s+(banaya|develop\s+kiya)|'
            r'aapko\s+kisne\s+(banaya|develop\s+kiya)|'
            r'kisne\s+(banaya|develop\s+kiya|banaya\s+hai)|'
            r'tumhara\s+(creator|developer|devloper|boss|malik)|'
            r'aapka\s+(creator|developer|devloper|boss|malik)|'
            r'kiska\s+assistant\s+ho)\b|'
            r'(किसने बनाया|तुम्हें किसने|आपको किसने|किसने डेवलप किया|किसका असिस्टेंट|तुम्हारा क्रिएटर|आपका क्रिएटर))',
            q,
            re.IGNORECASE
        ):
            if is_hindi_prompt:
                return "मैं जार्विस हूँ, एक हाई-टेक एआई सिस्टम जिसे आपकी सहायता के लिए तैयार किया गया है।"
            return "I am Jarvis, an advanced AI system built to assist you with all your macOS operations, sir."

        # 0.1 Identity queries
        if re.search(r'(\b(who are you|what is your name|tum kaun ho|aap kaun ho|naam kya hai)\b|(तुम कौन हो|आप कौन हो|तुम्हारा नाम क्या है|आपका नाम क्या है))', q, re.IGNORECASE):
            if is_hindi_prompt:
                return f"मैं {Config.ASSISTANT_NAME} हूँ, आपका पर्सनल एआई वॉइस असिस्टेंट।"
            return f"I am {Config.ASSISTANT_NAME}, your personal AI voice assistant, sir."

        # 1. Greetings & Well-being
        if re.search(r'\b(kaise ho|how are you|kaisa chal raha|kya haal hai|how do you do)\b', q):
            if is_hindi_prompt:
                return f"मैं पूरी क्षमता से कार्य कर रहा हूँ, {Config.USER_NAME}। बताइए मैं आपकी क्या सेवा करूँ?"
            return f"I am functioning at peak efficiency, {Config.USER_NAME}. How may I assist you today?"

        if re.search(r'\b(hello|namaste|hi|hey|good morning|good evening|good afternoon)\b', q):
            stripped_greeting = re.sub(r'\b(hello|namaste|hi|hey|good morning|good evening|jarvis)\b', '', q).strip()
            if not stripped_greeting:
                if is_hindi_prompt:
                    return f"नमस्ते {Config.USER_NAME}! सभी सिस्टम ऑनलाइन हैं। क्या हुक्म है?"
                return f"Hello {Config.USER_NAME}! All systems are online. How can I help you?"

        # Normalize query by stripping leading 'jarvis' variants
        q = re.sub(r'^(hey|hi|hello|ok|okay|oye|suno|arre)?\s*(jarvis|jarvish|jarves|javis|zarvis|jarvice|जार्विस)[,.]?\s*', '', q).strip()
        if not q:
            return f"जी {Config.USER_NAME}, मैं सुन रहा हूँ।" if is_hindi_prompt else f"Yes {Config.USER_NAME}, I am listening."

        # 2. Weather
        if re.search(r'\b(weather|mausam|temperature|rain|barish)\b', q):
            city_match = re.search(r'(?:in|for|of|at)\s+([a-zA-Z\s]+)', q)
            city = city_match.group(1).strip() if city_match else None
            return tools.get_weather(city)

        # 3. Time & Date
        if re.search(r'\b(time|date|din|baje|clock|samay|tarikh)\b', q):
            if any(w in q for w in ["what time", "current time", "time kya", "kitne baje", "today's date", "aaj kaun sa din", "date kya hai", "time please"]):
                return tools.get_time_and_date()

        # 4. Battery status
        if re.search(r'\b(battery|charging)\b', q):
            return tools.get_battery_status()

        # 5. System Health / Stats
        if re.search(r'\b(system status|system stats|cpu|ram|memory usage|mac health|performance)\b', q):
            return tools.get_system_stats()

        # 6. Volume controls
        vol_match = re.search(r'(?:set\s+)?volume\s+(?:to\s+)?(\d+)', q)
        if vol_match:
            return tools.set_volume(int(vol_match.group(1)))

        if re.search(r'\b(volume up|increase volume|volume badhao|sound badhao)\b', q):
            tools.adjust_volume(15)
            return "सर, आवाज़ बढ़ा दी गई है।" if is_hindi_prompt else "Volume increased, sir."

        if re.search(r'\b(volume down|decrease volume|volume kam karo|sound kam karo)\b', q):
            tools.adjust_volume(-15)
            return "सर, आवाज़ कम कर दी गई है।" if is_hindi_prompt else "Volume decreased, sir."

        if re.search(r'\b(mute|awaz band|quiet)\b', q):
            tools.mute_volume(True)
            return "आवाज़ म्यूट कर दी गई है, सर।" if is_hindi_prompt else "Audio muted, sir."

        if re.search(r'\b(unmute|awaz chalu)\b', q):
            tools.mute_volume(False)
            return "आवाज़ अनम्यूट कर दी गई है, सर।" if is_hindi_prompt else "Audio unmuted, sir."

        # 7. Media Playback Controls (Pause / Resume / Next)
        if re.search(r'\b(pause|stop music|gaana roko|pause song)\b', q):
            return tools.control_media("pause")
        if re.search(r'\b(resume|continue music|gaana chalu|play music)\b', q) and not any(w in q for w in ["youtube", "spotify"]):
            return tools.control_media("play")
        if re.search(r'\b(next song|skip song|agla gaana)\b', q):
            return tools.control_media("next")

        # 8. Screenshot
        if re.search(r'\b(screenshot|screen capture|screen shot)\b', q):
            name_match = re.search(r'(?:named|name|as)\s+([a-zA-Z0-9_\-]+)', q)
            custom_name = name_match.group(1) if name_match else None
            return tools.take_screenshot(custom_name)

        # 9. Lock screen / Sleep
        if re.search(r'\b(lock screen|lock mac|screen lock|screen band karo|sleep mac)\b', q):
            tools.lock_screen()
            return "स्क्रीन लॉक कर दी गई है, सर।" if is_hindi_prompt else "Screen locked, sir."

        # 10. Empty Trash
        if re.search(r'\b(empty trash|trash saaf|clear trash)\b', q):
            return tools.empty_trash()

        # 11. Music / YouTube Play Direct
        if any(q.startswith(w) for w in ["play", "chalao", "sunao", "baja do"]):
            target = re.sub(r'^(play|chalao|sunao|baja do)\s*', '', q)
            target = re.sub(r'\s+(song|gaana|music|on youtube|video)$', '', target).strip()
            if target.lower() in ["song", "songs", "gaana", "music", "a song", "some music", "some songs", ""]:
                return tools.play_youtube("trending top hits")
            return tools.play_youtube(target)

        if "youtube" in q and any(w in q for w in ["play", "chalao", "open", "kholo", "search"]):
            target = re.sub(r'.*?(?:play|search|chalao)\s+', '', q)
            target = re.sub(r'\s+(?:on|in)?\s*youtube.*', '', target).strip()
            if target and target != "youtube":
                return tools.play_youtube(target)
            return tools.open_website("youtube.com")

        # 12. Google Search
        if any(w in q for w in ["google search", "search google", "google pe search", "google karo"]):
            target = re.sub(r'.*?(?:google search|search google|google pe search|google karo)\s*(?:for|about)?\s*', '', q).strip()
            if target:
                return tools.search_google(target)
            return "गूगल पर क्या खोजना है, सर?" if is_hindi_prompt else "What would you like me to search for on Google?"

        if q.startswith("search ") or q.startswith("search for "):
            target = re.sub(r'^search\s+(for\s+)?', '', q).strip()
            if target:
                return tools.search_google(target)

        # 13. Wikipedia / Knowledge
        if any(q.startswith(w) for w in ["who is", "who was", "what is", "tell me about", "wikipedia"]):
            target = re.sub(r'^(who is|who was|what is|tell me about|wikipedia)\s*', '', q).strip()
            if target:
                return tools.search_wikipedia(target)

        # 14. Notes Management
        if any(w in q for w in ["read note", "read my note", "notes padho", "show notes", "list notes"]):
            return tools.read_notes()

        if any(w in q for w in ["take note", "make note", "write note", "note down", "note likho"]):
            content = re.sub(r'.*?(?:take note|make note|write note|note down|note likho)\s*(?:that|ki|about)?\s*', '', q).strip()
            if content:
                return tools.create_note(content)
            return "नोट में क्या लिखना है, सर?" if is_hindi_prompt else "What would you like me to write in the note, sir?"

        # 15. Jokes
        if re.search(r'\b(joke|hasao|chutkula|laugh)\b', q):
            return tools.tell_joke()

        # 16. Open Applications / Websites
        if any(q.startswith(w) for w in ["open", "launch", "start", "kholo", "run"]):
            target = re.sub(r'^(open|launch|start|kholo|run)\s*', '', q)
            target = re.sub(r'\s+(kholo|start karo|open karo)$', '', target).strip()
            
            web_domains = ["youtube", "google", "github", "chatgpt", "netflix", "gmail", "twitter", "reddit", "instagram", "whatsapp"]
            if any(dom == target or f"{dom}.com" == target for dom in web_domains):
                return tools.open_website(target)
                
            if re.search(r'\.(com|org|ai|io|net|dev|in|co)$', target):
                return tools.open_website(target)
                
            return tools.open_application(target)

        # 17. Close Application
        if any(q.startswith(w) for w in ["close", "quit", "band karo"]):
            target = re.sub(r'^(close|quit|band karo)\s*', '', q)
            target = re.sub(r'\s+(band karo|close karo)$', '', target).strip()
            return tools.close_application(target)

        # Default fallback
        if is_hindi_prompt:
            return f"जी {Config.USER_NAME}, मैंने सुना: '{raw_query}'। आप मुझसे यूट्यूब पर सीधे गाना चलाने, ऐप्स खोलने, मौसम देखने या स्क्रीनशॉट लेने को कह सकते हैं।"
        return (
            f"I understood: '{raw_query}'. "
            "You can ask me: 'open YouTube', 'play Bohemian Rhapsody', 'take screenshot', 'volume 70', 'check battery', "
            "'what is the weather in Mumbai', 'who is Albert Einstein', or 'tell me a joke'."
        )

brain = AssistantBrain()
