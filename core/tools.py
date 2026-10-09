import os
import sys
import re
import random
import datetime
import subprocess
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests
import psutil

from core.config import Config, NOTES_DIR, SCREENSHOTS_DIR

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

def open_url_or_file(target: str):
    """Universal cross-platform launcher for URLs, apps, or paths."""
    try:
        if IS_MACOS:
            subprocess.run(["open", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif IS_WINDOWS:
            os.startfile(target)
        else:
            subprocess.run(["xdg-open", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        webbrowser.open(target)

class SystemTools:
    """Core tool executor for Jarvis Assistant (macOS, Windows & Linux)."""

    @staticmethod
    def get_time_and_date() -> str:
        """Returns current time, date, and day of week."""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d, %Y")
        return f"It is currently {time_str} on {date_str}."

    @staticmethod
    def get_battery_status() -> str:
        """Checks battery level and charging status (cross-platform: macOS, Windows, Linux)."""
        try:
            battery = psutil.sensors_battery()
            if battery is not None:
                percentage = int(battery.percent)
                state = "charging" if battery.power_plugged else "discharging"
                return f"Battery is at {percentage} percent and currently {state}."
            
            # Fallback for macOS if psutil returned None
            if IS_MACOS:
                res = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True)
                match = re.search(r'(\d+)%;\s*([^;]+)', res.stdout)
                if match:
                    return f"Battery is at {match.group(1)} percent and currently {match.group(2).strip()}."
            
            return "Running on AC Power supply with no internal battery (Desktop PC), sir."
        except Exception as e:
            return f"Error retrieving battery status: {e}"

    @staticmethod
    def get_system_stats() -> str:
        """Returns CPU usage, RAM utilization, and disk space across Windows and macOS."""
        try:
            cpu = psutil.cpu_percent(interval=0.3)
            ram = psutil.virtual_memory()
            root_drive = (os.path.splitdrive(os.getcwd())[0] + os.sep) if IS_WINDOWS else '/'
            disk = psutil.disk_usage(root_drive)
            
            ram_free_gb = round(ram.available / (1024 ** 3), 1)
            disk_free_gb = round(disk.free / (1024 ** 3), 1)
            os_label = "Windows" if IS_WINDOWS else ("macOS" if IS_MACOS else "Linux")
            
            return (
                f"System Health ({os_label}): CPU utilization is at {cpu} percent. "
                f"RAM usage is {ram.percent} percent with {ram_free_gb} Gigabytes available. "
                f"Disk has {disk_free_gb} Gigabytes of free storage."
            )
        except Exception as e:
            return f"Error retrieving system stats: {e}"

    @staticmethod
    def set_volume(level: int) -> str:
        """Sets system volume (0-100) on macOS and Windows."""
        try:
            level = max(0, min(100, int(level)))
            if IS_MACOS:
                subprocess.run(["osascript", "-e", f"set volume output volume {level}"], check=True)
            elif IS_WINDOWS:
                # Windows volume adjustment
                ps_script = f"$w = New-Object -ComObject WScript.Shell; 1..50 | ForEach-Object {{ $w.SendKeys([char]174) }}; 1..{level // 2} | ForEach-Object {{ $w.SendKeys([char]175) }}"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
            return f"Volume set to {level} percent, sir."
        except Exception as e:
            return f"Failed to set volume: {e}"

    @staticmethod
    def adjust_volume(change: int) -> str:
        """Increases or decreases volume by a given delta across macOS and Windows."""
        try:
            direction = "increased" if change > 0 else "decreased"
            if IS_MACOS:
                res = subprocess.run(["osascript", "-e", "output volume of (get volume settings)"], capture_output=True, text=True)
                curr = int(res.stdout.strip())
                new_vol = max(0, min(100, curr + change))
                subprocess.run(["osascript", "-e", f"set volume output volume {new_vol}"], check=True)
                return f"Volume {direction} to {new_vol} percent, sir."
            elif IS_WINDOWS:
                key_code = 175 if change > 0 else 174
                steps = max(1, abs(change) // 4)
                ps_script = f"$w = New-Object -ComObject WScript.Shell; 1..{steps} | ForEach-Object {{ $w.SendKeys([char]{key_code}) }}"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
                return f"Volume {direction}, sir."
            return f"Adjusted volume {direction}, sir."
        except Exception as e:
            return f"Failed to adjust volume: {e}"

    @staticmethod
    def mute_volume(mute: bool = True) -> str:
        """Mutes or unmutes system audio across macOS and Windows."""
        try:
            if IS_MACOS:
                state = "true" if mute else "false"
                subprocess.run(["osascript", "-e", f"set volume output muted {state}"], check=True)
            elif IS_WINDOWS:
                # Key 173 is VK_VOLUME_MUTE
                ps_script = "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
            return "Volume muted, sir." if mute else "Audio unmuted, sir."
        except Exception as e:
            return f"Failed to toggle mute: {e}"

    @staticmethod
    def lock_screen() -> str:
        """Locks the screen on macOS and Windows."""
        try:
            if IS_MACOS:
                subprocess.run(["pmset", "displaysleepnow"])
            elif IS_WINDOWS:
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            else:
                subprocess.run(["xdg-screensaver", "lock"])
            return "Screen locked, sir."
        except Exception as e:
            return f"Failed to lock screen: {e}"

    @staticmethod
    def empty_trash() -> str:
        """Empties recycle bin / trash on macOS and Windows."""
        try:
            if IS_MACOS:
                subprocess.run(["osascript", "-e", 'tell application "Finder" to empty trash'], check=True)
            elif IS_WINDOWS:
                subprocess.run(["powershell", "-NoProfile", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"])
            return "Recycle bin / trash has been emptied, sir."
        except Exception as e:
            return f"Could not empty trash: {e}"

    @staticmethod
    def open_application(app_name: str) -> str:
        """Searches and opens an application across macOS and Windows."""
        if not app_name:
            return "Please specify an application name."
            
        app_name_clean = app_name.strip().lower()
        
        # Cross-platform common aliases mapping
        aliases = {
            "code": "code" if IS_WINDOWS else "Visual Studio Code",
            "vs code": "code" if IS_WINDOWS else "Visual Studio Code",
            "vscode": "code" if IS_WINDOWS else "Visual Studio Code",
            "chrome": "chrome" if IS_WINDOWS else "Google Chrome",
            "brave": "brave" if IS_WINDOWS else "Brave Browser",
            "browser": "msedge" if IS_WINDOWS else "Safari",
            "edge": "msedge",
            "settings": "ms-settings:" if IS_WINDOWS else "System Settings",
            "preferences": "ms-settings:" if IS_WINDOWS else "System Settings",
            "terminal": "wt" if IS_WINDOWS else "Terminal",
            "cmd": "cmd",
            "powershell": "powershell",
            "calc": "calc" if IS_WINDOWS else "Calculator",
            "calculator": "calc" if IS_WINDOWS else "Calculator",
            "files": "explorer" if IS_WINDOWS else "Finder",
            "explorer": "explorer",
            "finder": "explorer" if IS_WINDOWS else "Finder",
            "notepad": "notepad",
            "task manager": "taskmgr",
            "spotify": "spotify"
        }
        
        target = aliases.get(app_name_clean, app_name)
        
        if IS_WINDOWS:
            # 1. Try launching URI or direct Windows command
            try:
                if target.startswith("ms-settings:") or target in ["calc", "notepad", "explorer", "cmd", "wt", "powershell", "taskmgr"]:
                    os.system(f"start {target}")
                    return f"Opening {app_name.title()}, sir."
                ret = subprocess.run(["cmd", "/c", "start", "", target], capture_output=True, shell=True)
                if ret.returncode == 0:
                    return f"Opening {app_name.title()}, sir."
            except Exception:
                pass
                
            # 2. Search Windows Program Files and AppData
            win_dirs = [
                os.environ.get("ProgramFiles", "C:\\Program Files"),
                os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
                os.path.expanduser("~\\AppData\\Local"),
                os.path.expanduser("~\\AppData\\Roaming")
            ]
            for wdir in win_dirs:
                if os.path.exists(wdir):
                    for root, dirs, files in os.walk(wdir):
                        for f in files:
                            if f.lower().endswith(".exe") and app_name_clean in f.lower():
                                os.startfile(os.path.join(root, f))
                                return f"Opening {f[:-4].title()}, sir."
                        if root.count(os.sep) - wdir.count(os.sep) >= 2:
                            del dirs[:]
        else:
            # macOS launch sequence
            try:
                res = subprocess.run(["open", "-a", target], capture_output=True, text=True)
                if res.returncode == 0:
                    return f"Opening {target}, sir."
            except Exception:
                pass

            search_dirs = ["/Applications", "/System/Applications", "/System/Applications/Utilities", os.path.expanduser("~/Applications")]
            for sdir in search_dirs:
                if os.path.exists(sdir):
                    try:
                        for item in os.listdir(sdir):
                            if item.endswith(".app"):
                                name = item[:-4]
                                if app_name_clean == name.lower() or app_name_clean in name.lower():
                                    subprocess.run(["open", os.path.join(sdir, item)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                    return f"Opening {name}, sir."
                    except Exception:
                        continue

        # Universal fallback to web application
        web_fallbacks = {
            "spotify": "https://open.spotify.com",
            "chrome": "https://google.com",
            "whatsapp": "https://web.whatsapp.com",
            "netflix": "https://netflix.com",
            "youtube": "https://youtube.com",
            "instagram": "https://instagram.com",
            "chatgpt": "https://chatgpt.com",
            "github": "https://github.com",
            "twitter": "https://x.com",
            "x": "https://x.com"
        }
        if app_name_clean in web_fallbacks:
            open_url_or_file(web_fallbacks[app_name_clean])
            return f"Opening {app_name_clean.title()} in your browser, sir."

        return f"Could not locate application '{app_name}' on your system."

    @staticmethod
    def close_application(app_name: str) -> str:
        """Closes an open application on macOS or Windows."""
        try:
            if IS_WINDOWS:
                target_exe = app_name if app_name.lower().endswith(".exe") else f"{app_name}.exe"
                subprocess.run(["taskkill", "/IM", target_exe, "/F"], capture_output=True)
                return f"Closed {app_name}, sir."
            else:
                script = f'tell application "{app_name}" to quit'
                subprocess.run(["osascript", "-e", script], capture_output=True)
                return f"Closed {app_name}, sir."
        except Exception as e:
            return f"Could not close {app_name}: {e}"

    @staticmethod
    def open_website(url_or_domain: str) -> str:
        """Opens a website in the default browser across all operating systems."""
        target = url_or_domain.strip().lower()
        if not target.startswith("http://") and not target.startswith("https://"):
            if "." in target:
                target = "https://" + target
            else:
                target = f"https://www.{target}.com"
                
        open_url_or_file(target)
        return f"Opening {target} in your browser, sir."

    @staticmethod
    def search_google(query: str) -> str:
        """Performs a Google search in browser across all operating systems."""
        encoded = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded}"
        open_url_or_file(url)
        return f"Searching Google for '{query}', sir."

    @staticmethod
    def play_youtube(query: str) -> str:
        """Searches YouTube and directly plays the top matching video across all operating systems."""
        try:
            encoded = urllib.parse.quote(query)
            search_url = f"https://www.youtube.com/results?search_query={encoded}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            res = requests.get(search_url, headers=headers, timeout=5)
            if res.status_code == 200:
                video_ids = re.findall(r'\"videoId\":\"([a-zA-Z0-9_-]{11})\"', res.text)
                if video_ids:
                    direct_watch_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                    open_url_or_file(direct_watch_url)
                    return f"Playing '{query}' directly on YouTube, sir."

            # Fallback to search results
            open_url_or_file(search_url)
            return f"Playing '{query}' on YouTube, sir."
        except Exception:
            encoded = urllib.parse.quote(query)
            open_url_or_file(f"https://www.youtube.com/results?search_query={encoded}")
            return f"Playing '{query}' on YouTube, sir."

    @staticmethod
    def control_media(action: str) -> str:
        """Controls media playback (play, pause, next, previous) on macOS and Windows."""
        action_clean = action.lower().strip()
        
        if IS_WINDOWS:
            try:
                if "pause" in action_clean or "stop" in action_clean or "play" in action_clean or "resume" in action_clean:
                    ps_script = "(New-Object -ComObject WScript.Shell).SendKeys([char]179)"
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
                    return "Toggled media playback, sir."
                elif "next" in action_clean or "skip" in action_clean:
                    ps_script = "(New-Object -ComObject WScript.Shell).SendKeys([char]176)"
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
                    return "Skipped to next track, sir."
                elif "prev" in action_clean:
                    ps_script = "(New-Object -ComObject WScript.Shell).SendKeys([char]177)"
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
                    return "Playing previous track, sir."
                return f"Unknown media action: {action}"
            except Exception as e:
                return f"Could not adjust media playback: {e}"

        # macOS AppleScript media controls
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
        """Captures a screenshot and saves it to the screenshots directory across Windows and macOS."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if filename:
                name_clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', filename.strip())
                if not name_clean.endswith(".png"):
                    name_clean += ".png"
                file_path = SCREENSHOTS_DIR / name_clean
            else:
                file_path = SCREENSHOTS_DIR / f"screenshot_{timestamp}.png"
                
            # 1. Try cross-platform Pillow if available
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                img.save(str(file_path))
                return f"Screenshot captured and saved to {file_path.name}, sir."
            except Exception:
                pass

            # 2. Platform native fallback
            if IS_MACOS:
                res = subprocess.run(["screencapture", "-x", str(file_path)], capture_output=True, text=True)
                if res.returncode == 0:
                    return f"Screenshot captured and saved to {file_path.name}, sir."
                err = (res.stderr or "").lower()
                if "could not create image" in err or res.returncode == 1:
                    subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"])
                    return "Screen Recording permission required. I have opened System Settings for you, Sir."
            elif IS_WINDOWS:
                ps_cmd = (
                    "Add-Type -AssemblyName System.Windows.Forms,System.Drawing; "
                    "$b = New-Object Drawing.Bitmap([Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [Windows.Forms.Screen]::PrimaryScreen.Bounds.Height); "
                    "$g = [Drawing.Graphics]::FromImage($b); "
                    "$g.CopyFromScreen((New-Object Drawing.Point(0,0)), (New-Object Drawing.Point(0,0)), $b.Size); "
                    f"$b.Save('{str(file_path)}')"
                )
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)
                return f"Screenshot captured and saved to {file_path.name}, sir."

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

    @staticmethod
    def toggle_dark_mode(state: Optional[bool] = None) -> str:
        """Toggles or sets Dark Mode / Light Mode across macOS and Windows."""
        try:
            if IS_MACOS:
                if state is True:
                    script = 'tell application "System Events" to tell appearance preferences to set dark mode to true'
                elif state is False:
                    script = 'tell application "System Events" to tell appearance preferences to set dark mode to false'
                else:
                    script = 'tell application "System Events" to tell appearance preferences to set dark mode to not dark mode'
                subprocess.run(["osascript", "-e", script], check=True)
                return "Toggled system dark mode, sir."
            elif IS_WINDOWS:
                val = 0 if state is True else (1 if state is False else 0)
                ps_script = f"Set-ItemProperty -Path HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize -Name AppsUseLightTheme -Value {val} -Type DWord -Force -ErrorAction SilentlyContinue"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
                mode_str = "Dark" if val == 0 else "Light"
                return f"{mode_str} mode applied on Windows, sir."
            return "Appearance mode toggled, sir."
        except Exception as e:
            return f"Failed to toggle dark mode: {e}"

    @staticmethod
    def open_folder(folder_name: str) -> str:
        """Opens user folders (Downloads, Documents, Desktop, etc.) across macOS and Windows."""
        target = folder_name.lower().strip()
        home = Path.home()
        mapping = {
            "downloads": home / "Downloads",
            "documents": home / "Documents",
            "desktop": home / "Desktop",
            "pictures": home / "Pictures",
            "photos": home / "Pictures",
            "music": home / "Music",
            "movies": home / "Videos" if IS_WINDOWS else home / "Movies",
            "videos": home / "Videos" if IS_WINDOWS else home / "Movies",
            "home": home
        }
        if not IS_WINDOWS:
            mapping["applications"] = Path("/Applications")
            
        path = mapping.get(target)
        if not path:
            for k, p in mapping.items():
                if k in target or target in k:
                    path = p
                    break
        if not path:
            path = home / folder_name.strip()
            
        if path.exists():
            open_url_or_file(str(path))
            return f"Opening {path.name} folder, sir."
        return f"Could not find folder '{folder_name}' on your system."

    @staticmethod
    def copy_to_clipboard(text: str) -> str:
        """Copies text to system clipboard on macOS and Windows."""
        try:
            if IS_MACOS:
                subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            elif IS_WINDOWS:
                subprocess.run(["clip"], input=text.encode("utf-8"), check=True, shell=True)
            return "Copied to your clipboard, sir."
        except Exception as e:
            return f"Failed to copy to clipboard: {e}"

    @staticmethod
    def read_clipboard() -> str:
        """Reads content from system clipboard on macOS and Windows."""
        try:
            if IS_MACOS:
                res = subprocess.run(["pbpaste"], capture_output=True, text=True)
                content = res.stdout.strip()
            elif IS_WINDOWS:
                res = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], capture_output=True, text=True)
                content = res.stdout.strip()
            else:
                content = ""
            if not content:
                return "Your clipboard is currently empty, sir."
            return f"Clipboard contents: {content[:300]}"
        except Exception as e:
            return f"Failed to read clipboard: {e}"

    @staticmethod
    def calculate(expression: str) -> str:
        """Evaluates mathematical expressions safely."""
        import math
        expr = expression.lower().strip()
        expr = re.sub(r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)', r'(\1/100)*\2', expr)
        expr = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'(\1/100)', expr)
        expr = expr.replace('^', '**').replace('x', '*').replace('into', '*').replace('divided by', '/').replace('plus', '+').replace('minus', '-')
        clean_expr = re.sub(r'[^0-9\+\-\*\/\(\)\.\s]', '', expr)
        try:
            val = eval(clean_expr, {'__builtins__': None}, {'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'pi': math.pi})
            if isinstance(val, float) and val.is_integer():
                val = int(val)
            return f"The calculation result is {val}, sir."
        except Exception as e:
            return f"Could not calculate expression '{expression}': {e}"

    @staticmethod
    def find_files(filename_query: str) -> str:
        """Searches for files instantly across macOS (Spotlight) and Windows."""
        try:
            clean_q = filename_query.strip().replace('"', '')
            if IS_MACOS:
                res = subprocess.run(["mdfind", "-name", clean_q], capture_output=True, text=True, timeout=5)
                lines = [l.strip() for l in res.stdout.splitlines() if l.strip() and not l.startswith("2026-")]
                if not lines:
                    return f"No files found matching '{filename_query}', sir."
                top_matches = [Path(p).name for p in lines[:5]]
                return f"Found matching files: {', '.join(top_matches)}."
            elif IS_WINDOWS:
                ps_cmd = f"Get-ChildItem -Path $env:USERPROFILE -Filter '*{clean_q}*' -Recurse -Depth 3 -ErrorAction SilentlyContinue | Select-Object -First 5 -ExpandProperty Name"
                res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=8)
                lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
                if not lines:
                    return f"No files found matching '{filename_query}', sir."
                return f"Found matching files on your Windows PC: {', '.join(lines[:5])}."
            return f"Searched for '{filename_query}'."
        except Exception as e:
            return f"Search notice: {e}"

    @staticmethod
    def open_system_setting(setting_name: str) -> str:
        """Opens specific System Settings pane on macOS and Windows."""
        s = setting_name.lower().strip()
        if IS_WINDOWS:
            win_settings = {
                "wifi": "ms-settings:network-wifi",
                "wi-fi": "ms-settings:network-wifi",
                "bluetooth": "ms-settings:bluetooth",
                "display": "ms-settings:display",
                "displays": "ms-settings:display",
                "brightness": "ms-settings:display",
                "sound": "ms-settings:sound",
                "audio": "ms-settings:sound",
                "battery": "ms-settings:batterysaver",
                "wallpaper": "ms-settings:personalization-background",
                "privacy": "ms-settings:privacy",
                "security": "ms-settings:windowsdefender",
                "lock": "ms-settings:lockscreen"
            }
            target = win_settings.get(s, "ms-settings:")
            open_url_or_file(target)
            return f"Opened Windows Settings for '{setting_name}', sir."
        else:
            panes = {
                "wifi": "x-apple.systempreferences:com.apple.wifi-settings.extension",
                "wi-fi": "x-apple.systempreferences:com.apple.wifi-settings.extension",
                "bluetooth": "x-apple.systempreferences:com.apple.BluetoothSettings",
                "display": "x-apple.systempreferences:com.apple.Displays-Settings.extension",
                "displays": "x-apple.systempreferences:com.apple.Displays-Settings.extension",
                "brightness": "x-apple.systempreferences:com.apple.Displays-Settings.extension",
                "sound": "x-apple.systempreferences:com.apple.Sound-Settings.extension",
                "audio": "x-apple.systempreferences:com.apple.Sound-Settings.extension",
                "battery": "x-apple.systempreferences:com.apple.Battery-Settings.extension",
                "wallpaper": "x-apple.systempreferences:com.apple.Wallpaper-Settings.extension",
                "privacy": "x-apple.systempreferences:com.apple.preference.security",
                "security": "x-apple.systempreferences:com.apple.preference.security",
                "lock": "x-apple.systempreferences:com.apple.Lock-Screen-Settings.extension"
            }
            url = panes.get(s, "x-apple.systempreferences:com.apple.systempreferences")
            open_url_or_file(url)
            return f"Opened macOS System Settings for '{setting_name}', sir."

    @staticmethod
    def sleep_system() -> str:
        """Puts system to sleep across macOS and Windows."""
        try:
            if IS_MACOS:
                subprocess.Popen(["pmset", "sleepnow"])
            elif IS_WINDOWS:
                subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            return "Putting system to sleep, sir."
        except Exception as e:
            return f"Failed to put system to sleep: {e}"

    @staticmethod
    def sleep_mac() -> str:
        return SystemTools.sleep_system()

    @staticmethod
    def restart_system() -> str:
        """Restarts system across macOS and Windows."""
        try:
            if IS_MACOS:
                subprocess.run(["osascript", "-e", 'tell application "System Events" to restart'])
            elif IS_WINDOWS:
                subprocess.run(["shutdown", "/r", "/t", "5"])
            return "Initiating system restart, sir."
        except Exception as e:
            return f"Failed to restart system: {e}"

    @staticmethod
    def restart_mac() -> str:
        return SystemTools.restart_system()

    @staticmethod
    def shutdown_system() -> str:
        """Shuts down system across macOS and Windows."""
        try:
            if IS_MACOS:
                subprocess.run(["osascript", "-e", 'tell application "System Events" to shut down'])
            elif IS_WINDOWS:
                subprocess.run(["shutdown", "/s", "/t", "5"])
            return "Initiating system shutdown, sir."
        except Exception as e:
            return f"Failed to shut down system: {e}"

    @staticmethod
    def shutdown_mac() -> str:
        return SystemTools.shutdown_system()

tools = SystemTools()
