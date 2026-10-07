import os
import re
import random
import datetime
import subprocess
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests
import psutil

from core.config import Config, NOTES_DIR, SCREENSHOTS_DIR

class SystemTools:
    """Core tool executor for Jarvis Assistant on macOS."""

    @staticmethod
    def get_time_and_date() -> str:
        """Returns current time, date, and day of week."""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d, %Y")
        return f"It is currently {time_str} on {date_str}."

    @staticmethod
    def get_battery_status() -> str:
        """Checks macOS battery level and charging status."""
        try:
            res = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True)
            output = res.stdout
            # Example output: -InternalBattery-0 (id=23461987)	64%; charging; 2:09 remaining
            match = re.search(r'(\d+)%;\s*([^;]+)', output)
            if match:
                percentage = match.group(1)
                state = match.group(2).strip()
                return f"Battery is at {percentage} percent and currently {state}."
            return "Unable to determine precise battery details."
        except Exception as e:
            return f"Error retrieving battery status: {e}"

    @staticmethod
    def get_system_stats() -> str:
        """Returns CPU usage, RAM utilization, and disk space."""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            ram_free_gb = round(ram.available / (1024 ** 3), 1)
            disk_free_gb = round(disk.free / (1024 ** 3), 1)
            
            return (
                f"System Health: CPU utilization is at {cpu} percent. "
                f"RAM usage is {ram.percent} percent with {ram_free_gb} Gigabytes available. "
                f"Disk has {disk_free_gb} Gigabytes of free storage."
            )
        except Exception as e:
            return f"Error retrieving system stats: {e}"

    @staticmethod
    def set_volume(level: int) -> str:
        """Sets macOS system volume (0-100)."""
        try:
            level = max(0, min(100, int(level)))
            subprocess.run(["osascript", "-e", f"set volume output volume {level}"], check=True)
            return f"Volume set to {level} percent."
        except Exception as e:
            return f"Failed to set volume: {e}"

    @staticmethod
    def adjust_volume(change: int) -> str:
        """Increases or decreases volume by a given delta."""
        try:
            res = subprocess.run(["osascript", "-e", "output volume of (get volume settings)"], capture_output=True, text=True)
            curr = int(res.stdout.strip())
            new_vol = max(0, min(100, curr + change))
            subprocess.run(["osascript", "-e", f"set volume output volume {new_vol}"], check=True)
            direction = "increased" if change > 0 else "decreased"
            return f"Volume {direction} to {new_vol} percent."
        except Exception as e:
            return f"Failed to adjust volume: {e}"

    @staticmethod
    def mute_volume(mute: bool = True) -> str:
        """Mutes or unmutes system audio."""
        try:
            state = "true" if mute else "false"
            subprocess.run(["osascript", "-e", f"set volume output muted {state}"], check=True)
            return "Volume muted, sir." if mute else "Audio unmuted, sir."
        except Exception as e:
            return f"Failed to toggle mute: {e}"

    @staticmethod
    def lock_screen() -> str:
        """Locks the Mac screen."""
        try:
            # Modern macOS lock screen command
            subprocess.run(["pmset", "displaysleepnow"])
            return "Screen locked, sir."
        except Exception as e:
            return f"Failed to lock screen: {e}"

    @staticmethod
    def empty_trash() -> str:
        """Empties macOS trash."""
        try:
            subprocess.run(["osascript", "-e", 'tell application "Finder" to empty trash'], check=True)
            return "Trash has been emptied, sir."
        except Exception as e:
            return f"Could not empty trash: {e}"

    @staticmethod
    def open_application(app_name: str) -> str:
        """Searches and opens an application on macOS."""
        if not app_name:
            return "Please specify an application name."
            
        app_name_clean = app_name.strip().lower()
        
        # Common aliases mapping
        aliases = {
            "code": "Visual Studio Code",
            "vs code": "Visual Studio Code",
            "vscode": "Visual Studio Code",
            "chrome": "Google Chrome",
            "brave": "Brave Browser",
            "browser": "Safari",
            "settings": "System Settings",
            "preferences": "System Settings",
            "terminal": "Terminal",
            "calc": "Calculator",
            "files": "Finder"
        }
        
        target = aliases.get(app_name_clean, app_name)
        
        # Try direct open -a
        try:
            res = subprocess.run(["open", "-a", target], capture_output=True, text=True)
            if res.returncode == 0:
                return f"Opening {target}, sir."
        except Exception:
            pass

        # Search across Applications folders
        search_dirs = ["/Applications", "/System/Applications", "/System/Applications/Utilities", os.path.expanduser("~/Applications")]
        candidates = []
        for sdir in search_dirs:
            if os.path.exists(sdir):
                for item in os.listdir(sdir):
                    if item.endswith(".app"):
                        name = item[:-4]
                        if app_name_clean == name.lower():
                            subprocess.run(["open", os.path.join(sdir, item)])
                            return f"Opening {name}, sir."
                        elif app_name_clean in name.lower():
                            candidates.append((name, os.path.join(sdir, item)))
                            
        if candidates:
            # Pick closest candidate
            best_name, best_path = candidates[0]
            subprocess.run(["open", best_path])
            return f"Opening {best_name}, sir."
            
        return f"Could not locate application '{app_name}' on your Mac."

    @staticmethod
    def close_application(app_name: str) -> str:
        """Closes an open application on macOS."""
        try:
            script = f'tell application "{app_name}" to quit'
            subprocess.run(["osascript", "-e", script], capture_output=True)
            return f"Closed {app_name}, sir."
        except Exception as e:
            return f"Could not close {app_name}: {e}"

    @staticmethod
    def open_website(url_or_domain: str) -> str:
        """Opens a website in the default browser."""
        target = url_or_domain.strip().lower()
        if not target.startswith("http://") and not target.startswith("https://"):
            if "." in target:
                target = "https://" + target
            else:
                target = f"https://www.{target}.com"
                
        subprocess.run(["open", target])
        return f"Opening {target} in your browser."

    @staticmethod
    def search_google(query: str) -> str:
        """Performs a Google search in browser."""
        encoded = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded}"
        subprocess.run(["open", url])
        return f"Searching Google for '{query}'."

    @staticmethod
    def play_youtube(query: str) -> str:
        """Searches YouTube and directly plays the top matching video."""
        try:
            encoded = urllib.parse.quote(query)
            search_url = f"https://www.youtube.com/results?search_query={encoded}"
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
            
            res = requests.get(search_url, headers=headers, timeout=5)
            if res.status_code == 200:
                video_ids = re.findall(r'\"videoId\":\"([a-zA-Z0-9_-]{11})\"', res.text)
                if video_ids:
                    direct_watch_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                    subprocess.run(["open", direct_watch_url])
                    return f"Playing '{query}' directly on YouTube, sir."

            # Fallback to search results
            subprocess.run(["open", search_url])
            return f"Playing '{query}' on YouTube, sir."
        except Exception:
            encoded = urllib.parse.quote(query)
            subprocess.run(["open", f"https://www.youtube.com/results?search_query={encoded}"])
            return f"Playing '{query}' on YouTube, sir."

    @staticmethod
    def control_media(action: str) -> str:
        """Controls media playback (play, pause, next, previous) on macOS."""
        action_clean = action.lower().strip()
        script = ""
        
        if "pause" in action_clean or "stop" in action_clean:
            script = '''
            try
                tell application "Spotify" to pause
            end try
            try
                tell application "Music" to pause
            end try
            '''
            desc = "Paused media playback, sir."
        elif "play" in action_clean or "resume" in action_clean:
            script = '''
            try
                tell application "Spotify" to play
            end try
            try
                tell application "Music" to play
            end try
            '''
            desc = "Resumed media playback, sir."
        elif "next" in action_clean or "skip" in action_clean:
            script = '''
            try
                tell application "Spotify" to next track
            end try
            try
                tell application "Music" to next track
            end try
            '''
            desc = "Skipped to next track, sir."
        elif "prev" in action_clean:
            script = '''
            try
                tell application "Spotify" to previous track
            end try
            try
                tell application "Music" to previous track
            end try
            '''
            desc = "Playing previous track, sir."
        else:
            return f"Unknown media action: {action}"

        try:
            subprocess.run(["osascript", "-e", script], check=True)
            return desc
        except Exception as e:
            return f"Could not adjust media playback: {e}"

    @staticmethod
    def search_wikipedia(query: str) -> str:
        """Fetches a concise factual summary from Wikipedia."""
        try:
            headers = {"User-Agent": "JarvisAI/2.0 (Contact: support@jarvis.ai)"}
            clean_query = query.strip().replace(" ", "_")
            api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_query}"
            
            res = requests.get(api_url, headers=headers, timeout=6)
            if res.status_code == 200:
                data = res.json()
                title = data.get("title", query)
                extract = data.get("extract", "")
                if extract:
                    # Keep to 2 sentences for concise speech
                    sentences = extract.split(". ")
                    short_summary = ". ".join(sentences[:2]) + "."
                    return f"According to Wikipedia: {short_summary}"
                    
            # Fallback search if exact title wasn't found
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=1&namespace=0&format=json"
            s_res = requests.get(search_url, headers=headers, timeout=6).json()
            if len(s_res) > 2 and s_res[2] and s_res[2][0]:
                return f"According to Wikipedia: {s_res[2][0]}"
                
            return f"I couldn't find a direct Wikipedia article for '{query}'."
        except Exception as e:
            return f"Error querying Wikipedia: {e}"

    @staticmethod
    def take_screenshot(filename: Optional[str] = None) -> str:
        """Captures a screenshot and saves it to the screenshots directory."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if filename:
                name_clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', filename.strip())
                if not name_clean.endswith(".png"):
                    name_clean += ".png"
                file_path = SCREENSHOTS_DIR / name_clean
            else:
                file_path = SCREENSHOTS_DIR / f"screenshot_{timestamp}.png"
                
            res = subprocess.run(["screencapture", "-x", str(file_path)], capture_output=True, text=True)
            if res.returncode != 0:
                err = (res.stderr or "").lower()
                # On macOS, 'could not create image from display' means Screen Recording permission is missing
                if "could not create image" in err or res.returncode == 1:
                    # Automatically open Privacy & Security -> Screen Recording
                    subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"])
                    return (
                        "Screen Recording permission is required by macOS. "
                        "I have opened System Settings for you, Sir. Please toggle 'Terminal' ON, "
                        "then try the command again."
                    )
                return f"Could not capture screenshot: {res.stderr.strip()}"
                
            return f"Screenshot captured and saved to {file_path.name}, sir."
        except Exception as e:
            return f"Failed to take screenshot: {e}"

    @staticmethod
    def create_note(content: str, title: Optional[str] = None) -> str:
        """Saves a note in text format."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            date_header = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if not title:
                title = f"note_{timestamp}"
            else:
                title = re.sub(r'[^a-zA-Z0-9_\-]', '_', title.strip())
                
            note_file = NOTES_DIR / f"{title}.txt"
            
            with open(note_file, "a", encoding="utf-8") as f:
                f.write(f"\n--- {date_header} ---\n{content}\n")
                
            return f"Note recorded in '{title}.txt'."
        except Exception as e:
            return f"Failed to save note: {e}"

    @staticmethod
    def read_notes(title: Optional[str] = None) -> str:
        """Reads back saved notes."""
        try:
            if not NOTES_DIR.exists():
                return "No notes directory found."
                
            note_files = sorted(list(NOTES_DIR.glob("*.txt")), key=os.path.getmtime, reverse=True)
            if not note_files:
                return "You have no saved notes yet, sir."
                
            if title:
                match = [f for f in note_files if title.lower() in f.stem.lower()]
                if match:
                    content = match[0].read_text(encoding="utf-8")
                    return f"Contents of {match[0].stem}: {content}"
                return f"Could not find note matching '{title}'."
                
            # Read most recent note
            latest = note_files[0]
            content = latest.read_text(encoding="utf-8")
            return f"Your latest note in {latest.stem} says: {content}"
        except Exception as e:
            return f"Failed to read notes: {e}"

    @staticmethod
    def list_notes() -> str:
        """Lists all existing notes."""
        try:
            notes = list(NOTES_DIR.glob("*.txt"))
            if not notes:
                return "You have no saved notes."
            names = [f.stem for f in notes]
            return f"You have {len(names)} notes: {', '.join(names[:5])}."
        except Exception as e:
            return f"Failed to list notes: {e}"

    @staticmethod
    def get_weather(city: Optional[str] = None) -> str:
        """Gets live real-time weather from Open-Meteo."""
        try:
            target_city = city.strip() if city else Config.DEFAULT_CITY
            
            # Geocoding
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(target_city)}&count=1"
            geo_res = requests.get(geo_url, timeout=5).json()
            
            if not geo_res.get("results"):
                return f"Could not find coordinates for '{target_city}'."
                
            loc = geo_res["results"][0]
            lat, lon = loc["latitude"], loc["longitude"]
            city_name = loc.get("name", target_city)
            country = loc.get("country", "")
            
            # Forecast
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            )
            w_res = requests.get(weather_url, timeout=5).json()
            curr = w_res.get("current", {})
            temp = curr.get("temperature_2m", "N/A")
            humidity = curr.get("relative_humidity_2m", "N/A")
            wind = curr.get("wind_speed_10m", "N/A")
            code = curr.get("weather_code", 0)
            
            conditions = {
                0: "Clear skies", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Foggy", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
                80: "Rain showers", 95: "Thunderstorm"
            }
            condition_desc = conditions.get(code, "Pleasant")
            
            return (
                f"In {city_name}, {country}, it is currently {condition_desc} with a temperature "
                f"of {temp} degrees Celsius, humidity at {humidity} percent, and winds at {wind} kilometers per hour."
            )
        except Exception as e:
            return f"Could not retrieve weather data: {e}"

    @staticmethod
    def tell_joke() -> str:
        """Tells a humorous programming or assistant joke."""
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs, sir.",
            "There are 10 types of people in the world: those who understand binary, and those who don't.",
            "Why was the JavaScript developer sad? Because they didn't know how to 'null' their feelings.",
            "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
            "Why do Python programmers have low vision? Because they can't C.",
            "An optimist says the glass is half full. A pessimist says it's half empty. A programmer says the glass is twice as large as necessary."
        ]
        return random.choice(jokes)

    @staticmethod
    def execute_terminal_command(command: str) -> str:
        """Executes safe local commands like git, ls, ping, etc."""
        # Security blacklist
        dangerous = ["rm -rf", "mkfs", "dd", "> /dev/", ":(){ :|:& };:"]
        for d in dangerous:
            if d in command:
                return "Command blocked for system safety, sir."
                
        try:
            res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            out = res.stdout.strip() or res.stderr.strip()
            if not out:
                return "Command completed with no output."
            # Truncate if too long
            return out[:400]
        except subprocess.TimeoutExpired:
            return "Command timed out after 10 seconds."
        except Exception as e:
            return f"Execution error: {e}"

    @staticmethod
    def make_phone_call(contact_or_number: str) -> str:
        """Calls a contact or phone number via FaceTime audio / iPhone cellular calling."""
        from core.contacts import contacts_mgr
        return contacts_mgr.make_call(contact_or_number)

    @staticmethod
    def send_text_message(recipient: str, message: str, platform: str = "messages") -> str:
        """Sends an SMS/iMessage or WhatsApp message to a recipient or phone number."""
        from core.contacts import contacts_mgr
        return contacts_mgr.send_text(recipient, message, platform)

    @staticmethod
    def add_contact(name: str, phone: str) -> str:
        """Saves a new contact to Jarvis address book."""
        from core.contacts import contacts_mgr
        return contacts_mgr.add_contact(name, phone)

tools = SystemTools()
