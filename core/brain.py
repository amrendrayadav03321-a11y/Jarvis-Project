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
                tools.make_phone_call,
                tools.send_text_message,
                tools.add_contact,
                tools.toggle_dark_mode,
                tools.open_folder,
                tools.copy_to_clipboard,
                tools.read_clipboard,
                tools.calculate,
                tools.find_files,
                tools.open_system_setting,
                tools.sleep_mac,
                tools.restart_mac,
                tools.shutdown_mac,
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
                "   - You have complete control over macOS. When the user asks for ANY command or task, DO NOT talk or give disclaimers—IMMEDIATELY CALL THE APPROPRIATE TOOL.\n"
                "   - For music requests ('play Kesariya', 'gaana chalao', 'Arijit Singh song'), call 'play_youtube'.\n"
                "   - For phone calls ('call Rohit', 'Papa ko call karo', 'call 9876543210'), call 'make_phone_call'.\n"
                "   - For text messages ('text Rohit I am late', 'Papa ko message bhejo', 'WhatsApp Aman'), call 'send_text_message'.\n"
                "   - For applications/websites ('open Chrome', 'Spotify kholo', 'open YouTube'), call 'open_application' or 'open_website'.\n"
                "   - For folders ('downloads folder kholo'), call 'open_folder'.\n"
                "   - For dark mode ('dark mode on karo'), call 'toggle_dark_mode'.\n"
                "   - For calculations ('calculate 500 * 24'), call 'calculate'.\n"
                "   - For system controls (volume, screen lock, screenshot, clipboard, battery, weather), call the corresponding tool.\n"
                "   - Keep spoken answers brief (1 or 2 crisp sentences) so they are fast and conversational over voice."
            )
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=tool_list,
                temperature=0.7
            )
            
            models_to_try = [Config.GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest", "gemini-2.5-flash"]
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
        """Processes user input using Fast-Path Local Execution for sub-10ms responses,
        and falls back to Gemini LLM for open-ended conversation and complex questions.
        """
        if not query or not query.strip():
            return ""

        query_clean = query.strip()

        # 1. FAST-PATH: Instant local execution (<10ms) for all system actions & tools
        local_result = self._match_and_execute_local(query_clean)
        if local_result is not None:
            return local_result

        # 2. AI-PATH: Send open-ended knowledge & chat queries to Google Gemini LLM
        if self.is_gemini_active and self.chat_session:
            try:
                response = self.chat_session.send_message(query_clean)
                if response and response.text:
                    return response.text.strip()
            except Exception:
                pass

        # 3. Fallback when Gemini is offline or unavailable
        return self._process_offline_fallback(query_clean)

    def _match_and_execute_local(self, raw_query: str) -> Optional[str]:
        """High-accuracy multi-lingual local action matching in English & Hinglish.
        Returns the action result string if matched, or None for general AI queries.
        """
        q = raw_query.lower().strip()
        is_hindi_prompt = bool(re.search(r'[\u0900-\u097F]', raw_query)) or any(
            w in q for w in ["karo", "kholo", "chalao", "sunao", "batao", "kaise", "kya", "kitni", "hai", "likho", "saaf", "gaana", "roko", "kisne", "badhao"]
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
        q = re.sub(r'^(hey|hi|hello|ok|okay|oye|suno|arre)?\s*(jarvis|jarvish|jarves|javis|zarvis|jarvice|service|sarvis|travis|जार्विस|सर्विस)[,.]?\s*', '', q).strip()
        if not q:
            from core.wakeword import wake_detector
            return wake_detector.get_acknowledgement(raw_query)

        # 1.5 Calling & Dialing (FaceTime Audio / Native Phone)
        target_call = None
        m_call = re.search(r'([a-zA-Z0-9_\+\s]+?)\s+ko\s+(?:call|phone)\s*(?:lagao|karo|milao)?', q)
        if m_call:
            target_call = m_call.group(1).strip()
        else:
            m_call = re.search(r'(?:phone|call)\s*(?:lagao|karo|milao)\s+([a-zA-Z0-9_\+\s]+?)(?:\s+ko)?$', q)
            if m_call:
                target_call = m_call.group(1).strip()
            else:
                m_call = re.search(r'\b(?:call|dial|phone)\s+(?:to\s+)?([a-zA-Z0-9_\+]+)', q)
                if m_call:
                    t_cand = m_call.group(1).strip()
                    if t_cand.lower() not in ["lagao", "karo", "milao", "up", "down", "back", "off"]:
                        target_call = t_cand

        if target_call:
            target_call = re.sub(r'^(please|zara)\s+', '', target_call).strip()
            if target_call:
                return tools.make_phone_call(target_call)

        # 1.6 Text Messaging, SMS, & WhatsApp
        is_wa = "whatsapp" in q
        m_msg = re.search(r'([a-zA-Z0-9_\+\s]+?)\s+ko\s+(?:whatsapp|message|text|sms)\s*(?:par\s+)?(?:bhejo|karo)\s*(?:ki\s+)?(.*)', q)
        if not m_msg:
            m_msg = re.search(r'(?:whatsapp|message|text|sms)\s*(?:par\s+)?(?:bhejo|karo)\s+([a-zA-Z0-9_\+\s]+?)\s+ko\s*(?:ki\s+)?(.*)', q)
        if not m_msg:
            m_msg = re.search(r'(?:text|message|sms|whatsapp|send message to)\s+([a-zA-Z0-9_\+]+)\s+(?:saying\s+|that\s+|ki\s+)?(.*)', q)

        if m_msg:
            target_person = m_msg.group(1).strip()
            message_body = m_msg.group(2).strip()
            platform = "whatsapp" if is_wa else "messages"
            return tools.send_text_message(target_person, message_body, platform)

        # 1.7 Add / Save Contact
        save_match = re.search(r'(?:save contact|add contact)\s+([a-zA-Z\s]+)\s+(?:number\s+)?([0-9\+]+)', q)
        if not save_match:
            save_match = re.search(r'([a-zA-Z\s]+)\s+ka\s+number\s+([0-9\+]+)\s+(?:save|add)\s*karo', q)
        if save_match:
            c_name = save_match.group(1).strip()
            c_num = save_match.group(2).strip()
            return tools.add_contact(c_name, c_num)

        # 0. Presentation & Call Mode Toggle
        if any(w in q for w in ["presentation mode on", "call mode on", "demo mode on", "conference mode on", "presentation mode chalu"]):
            from core.listener import listener
            listener.set_presentation_mode(True)
            return f"Presentation Mode activated, {Config.USER_NAME}. Acoustic filters are armed for conference calls."

        if any(w in q for w in ["presentation mode off", "call mode off", "demo mode off", "exit presentation mode", "normal mode"]):
            from core.listener import listener
            listener.set_presentation_mode(False)
            return f"Presentation Mode deactivated, {Config.USER_NAME}. Standard acoustic mode restored."

        # 2. Weather
        if re.search(r'\b(weather|mausam|temperature|rain|barish)\b', q):
            city_match = re.search(r'\b(?:in|for|of)\s+([a-zA-Z\s]+)', q)
            city = city_match.group(1).strip() if city_match else None
            return tools.get_weather(city)

        # 3. Time & Date
        if re.search(r'\b(time|date|din|baje|clock|samay|tarikh)\b', q):
            if any(w in q for w in ["what time", "current time", "time kya", "kitne baje", "today's date", "aaj kaun sa din", "date kya hai", "time please", "samay kya"]):
                return tools.get_time_and_date()

        # 4. Battery status
        if re.search(r'\b(battery|charging|charge)\b', q):
            return tools.get_battery_status()

        # 5. System Health / Stats
        if re.search(r'\b(system status|system stats|cpu|ram|memory usage|mac health|performance)\b', q):
            return tools.get_system_stats()

        # 6. Dark Mode / Light Mode
        if re.search(r'\b(dark mode|light mode)\b', q):
            if any(w in q for w in ["on", "enable", "chalu", "lagao"]):
                return tools.toggle_dark_mode(True)
            elif any(w in q for w in ["off", "disable", "hatao", "band"]):
                return tools.toggle_dark_mode(False)
            return tools.toggle_dark_mode(None)

        # 7. Volume controls (English & Hindi)
        vol_match = re.search(r'(?:set\s+)?volume\s+(?:to\s+)?(\d+)', q)
        if vol_match:
            return tools.set_volume(int(vol_match.group(1)))

        if re.search(r'\b(volume up|increase volume|volume badhao|sound badhao|awaaz badhao|awaz badhao)\b', q):
            tools.adjust_volume(15)
            return "सर, आवाज़ बढ़ा दी गई है।" if is_hindi_prompt else "Volume increased, sir."

        if re.search(r'\b(volume down|decrease volume|volume kam karo|sound kam karo|awaaz kam karo|awaz kam karo)\b', q):
            tools.adjust_volume(-15)
            return "सर, आवाज़ कम कर दी गई है।" if is_hindi_prompt else "Volume decreased, sir."

        if re.search(r'\b(mute|awaz band|awaaz band|quiet)\b', q):
            tools.mute_volume(True)
            return "आवाज़ म्यूट कर दी गई है, सर।" if is_hindi_prompt else "Audio muted, sir."

        if re.search(r'\b(unmute|awaz chalu|awaaz chalu)\b', q):
            tools.mute_volume(False)
            return "आवाज़ अनम्यूट कर दी गई है, सर।" if is_hindi_prompt else "Audio unmuted, sir."

        # 8. Media Playback Controls (Pause / Resume / Next)
        if re.search(r'\b(pause|stop music|gaana roko|pause song|gana roko)\b', q):
            return tools.control_media("pause")
        if re.search(r'\b(resume|continue music|gaana chalu|gana chalu)\b', q):
            return tools.control_media("play")
        if re.search(r'\b(next song|skip song|agla gaana|agla gana)\b', q):
            return tools.control_media("next")

        # 9. Screenshot
        if re.search(r'\b(screenshot|screen capture|screen shot|screenshot lo|screenshot kheencho)\b', q):
            name_match = re.search(r'(?:named|name|as)\s+([a-zA-Z0-9_\-]+)', q)
            custom_name = name_match.group(1) if name_match else None
            return tools.take_screenshot(custom_name)

        # 10. Screen Lock / Mac Sleep / Restart / Shutdown
        if re.search(r'\b(lock screen|lock mac|screen lock|screen band karo|laptop lock)\b', q):
            tools.lock_screen()
            return "स्क्रीन लॉक कर दी गई है, सर।" if is_hindi_prompt else "Screen locked, sir."
        if re.search(r'\b(sleep mac|mac sleep|laptop sleep|mac ko sula do)\b', q):
            return tools.sleep_mac()
        if re.search(r'\b(restart mac|reboot mac|mac restart karo)\b', q):
            return tools.restart_mac()
        if re.search(r'\b(shutdown mac|shut down mac|mac shut down|mac band karo)\b', q):
            return tools.shutdown_mac()

        # 11. Empty Trash
        if re.search(r'\b(empty trash|trash saaf|clear trash)\b', q):
            return tools.empty_trash()

        # 12. Open Folder in Finder
        m_folder = re.search(r'(?:open\s+)?\b(downloads|documents|desktop|pictures|music|movies|applications)\b(?:\s+folder)?(?:\s+(?:kholo|open karo))?', q)
        if m_folder and any(w in q for w in ["folder", "downloads", "documents", "desktop", "kholo", "open"]):
            return tools.open_folder(m_folder.group(1))

        # 13. System Settings Panes
        if re.search(r'\b(settings|preferences)\b', q):
            pane_match = re.search(r'\b(wifi|wi-fi|bluetooth|display|displays|brightness|sound|battery|wallpaper|privacy)\b', q)
            pane = pane_match.group(1) if pane_match else "general"
            return tools.open_system_setting(pane)

        # 14. Clipboard Copy & Read
        if any(w in q for w in ["clipboard copy", "copy to clipboard", "clipboard par copy"]):
            text_to_copy = re.sub(r'.*?(?:clipboard copy|copy to clipboard|clipboard par copy)\s*(?:karo)?\s*', '', q).strip()
            if text_to_copy:
                return tools.copy_to_clipboard(text_to_copy)
        if any(w in q for w in ["read clipboard", "clipboard read", "clipboard dikhao", "clipboard par kya hai"]):
            return tools.read_clipboard()

        # 15. Math & Calculator
        if any(w in q for w in ["calculate", "hisab karo", "kitna hota hai"]) or re.search(r'^\s*\d+[\d\s\+\-\*\/\%\^\.x]+\s*$', q):
            clean_math = re.sub(r'.*?(?:calculate|hisab karo)\s*', '', q)
            clean_math = re.sub(r'\s*kitna hota hai.*', '', clean_math).strip()
            return tools.calculate(clean_math)

        # 16. Spotlight File Search
        if any(w in q for w in ["find file", "search file", "file dhoondo", "locate file"]):
            f_target = re.sub(r'.*?(?:find file|search file|file dhoondo|locate file)\s*', '', q).strip()
            if f_target:
                return tools.find_files(f_target)

        # 17. Music / YouTube Play Direct (Hindi verb-final + English verb-initial)
        m_music = re.search(r'^(?:play|chalao|bajao|sunao|lagao)\s+(.+)', q)
        if not m_music:
            m_music = re.search(r'(.+?)\s+(?:gaana|gana|song|music|video)\s*(?:chalao|bajao|sunao|lagao|play karo|play)?$', q)
        if not m_music:
            m_music = re.search(r'(.+?)\s+(?:chalao|bajao|sunao|lagao)$', q)
            
        if m_music:
            song_target = m_music.group(1).strip()
            song_target = re.sub(r'^(please|zara|koi|koi accha|koi badhiya)\s+', '', song_target).strip()
            song_target = re.sub(r'\s+(song|gaana|gana|music|on youtube|video)$', '', song_target).strip()
            if song_target in ["", "song", "gaana", "gana", "music", "songs"]:
                return tools.play_youtube("trending top hits")
            return tools.play_youtube(song_target)

        # 18. Google Search
        if any(w in q for w in ["google search", "search google", "google pe search", "google karo"]):
            target = re.sub(r'.*?(?:google search|search google|google pe search|google karo)\s*(?:for|about)?\s*', '', q).strip()
            if target:
                return tools.search_google(target)
            return "गूगल पर क्या खोजना है, सर?" if is_hindi_prompt else "What would you like me to search for on Google?"

        if q.startswith("search ") or q.startswith("search for "):
            target = re.sub(r'^search\s+(for\s+)?', '', q).strip()
            if target:
                return tools.search_google(target)

        # 19. Wikipedia / Knowledge
        if any(q.startswith(w) for w in ["who is", "who was", "what is", "tell me about", "wikipedia"]):
            target = re.sub(r'^(who is|who was|what is|tell me about|wikipedia)\s*', '', q).strip()
            if target:
                return tools.search_wikipedia(target)

        # 20. Notes Management
        if any(w in q for w in ["read note", "read my note", "notes padho", "show notes", "list notes"]):
            return tools.read_notes()

        if any(w in q for w in ["take note", "make note", "write note", "note down", "note likho"]):
            content = re.sub(r'.*?(?:take note|make note|write note|note down|note likho)\s*(?:that|ki|about)?\s*', '', q).strip()
            if content:
                return tools.create_note(content)
            return "नोट में क्या लिखना है, सर?" if is_hindi_prompt else "What would you like me to write in the note, sir?"

        # 21. Jokes
        if re.search(r'\b(joke|hasao|chutkula|laugh)\b', q):
            return tools.tell_joke()

        # 22. Open Applications & Websites (Handles 'chrome kholo', 'open chrome', 'spotify open karo')
        m_open = re.search(r'^(?:open|launch|start|kholo|run)\s+(.+)', q)
        if not m_open:
            m_open = re.search(r'(.+?)\s+(?:kholo|open karo|start karo|chalu karo|run karo)$', q)
            
        if m_open:
            app_target = m_open.group(1).strip()
            app_target = re.sub(r'^(please|zara)\s+', '', app_target).strip()
            
            web_domains = ["youtube", "google", "github", "chatgpt", "netflix", "gmail", "twitter", "reddit", "instagram", "whatsapp"]
            if any(dom == app_target or f"{dom}.com" == app_target for dom in web_domains):
                return tools.open_website(app_target)
                
            if re.search(r'\.(com|org|ai|io|net|dev|in|co)$', app_target):
                return tools.open_website(app_target)
                
            return tools.open_application(app_target)

        # 23. Close Application (Handles 'chrome band karo', 'close chrome', 'spotify quit karo')
        m_close = re.search(r'^(?:close|quit|band karo|exit)\s+(.+)', q)
        if not m_close:
            m_close = re.search(r'(.+?)\s+(?:band karo|close karo|quit karo)$', q)
            
        if m_close:
            close_target = m_close.group(1).strip()
            return tools.close_application(close_target)

        # If no local action matched, return None so process() hands it over to Gemini AI
        return None

    def _process_offline_fallback(self, raw_query: str) -> str:
        """Smart fallback when query is not a local action and Gemini is unavailable."""
        q = raw_query.lower().strip()
        is_hindi = bool(re.search(r'[\u0900-\u097F]', raw_query)) or any(
            w in q for w in ["karo", "kya", "kaise", "batao", "kahan", "kyun"]
        )
        if len(q.split()) > 1 and any(w in q for w in ["who", "what", "where", "how", "why", "kahan", "kaise", "kyun"]):
            return tools.search_google(raw_query)

        if is_hindi:
            return f"जी {Config.USER_NAME}, मैंने सुना: '{raw_query}'। आप मुझसे यूट्यूब पर गाना चलाने, ऐप्स खोलने, मौसम देखने, कॉल करने या स्क्रीनशॉट लेने को कह सकते हैं।"
        return (
            f"I understood: '{raw_query}'. "
            "You can ask me: 'open Chrome', 'play Kesariya', 'call Papa', 'take screenshot', 'volume 70', 'check battery', "
            "or 'dark mode on'."
        )

    def _process_offline_intent(self, raw_query: str) -> str:
        """Backwards-compatibility alias for tests and direct offline evaluation."""
        res = self._match_and_execute_local(raw_query)
        if res is not None:
            return res
        return self._process_offline_fallback(raw_query)

brain = AssistantBrain()
