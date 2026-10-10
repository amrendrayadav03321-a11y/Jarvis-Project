import os
import sys
import time
import socket
import psutil
import asyncio
import threading
import subprocess
import webbrowser
from pathlib import Path
from aiohttp import web

from core.config import Config
from core.speaker import speaker
from core.listener import listener
from core.brain import brain
from core.wakeword import wake_detector

WEB_DIR = Path(__file__).resolve().parent / "web"

def get_local_ip() -> str:
    """Returns local network IP address for cross-device access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

class JarvisServer:
    def __init__(self, port: int = 8888):
        self.port = port
        self.local_ip = get_local_ip()
        self.app = web.Application()
        self.messages = [
            {
                "role": "jarvis",
                "text": f"Jarvis Mark 85 online. All tactical protocols armed and ready, {Config.USER_NAME}. Standing by for your directive.",
                "time": time.strftime("%H:%M:%S")
            }
        ]
        self.voice_state = "standby"  # standby | listening | processing | speaking
        self.voice_thread = None
        self.running = True
        self._setup_routes()

    def _setup_routes(self):
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/api/status", self.handle_status)
        self.app.router.add_get("/api/history", self.handle_history)
        self.app.router.add_get("/api/presentation", self.handle_get_presentation)
        self.app.router.add_post("/api/presentation", self.handle_toggle_presentation)
        self.app.router.add_post("/api/command", self.handle_command)
        self.app.router.add_post("/api/listen", self.handle_manual_listen)
        self.app.router.add_static("/", path=str(WEB_DIR), name="static")

    async def handle_get_presentation(self, request):
        return web.json_response({"presentation_mode": listener.presentation_mode})

    async def handle_toggle_presentation(self, request):
        try:
            data = await request.json()
        except Exception:
            data = {}
        target = data.get("enabled", not listener.presentation_mode)
        listener.set_presentation_mode(bool(target))
        Config.PRESENTATION_MODE = bool(target)
        return web.json_response({"presentation_mode": listener.presentation_mode})

    async def handle_index(self, request):
        return web.FileResponse(WEB_DIR / "index.html")

    async def handle_status(self, request):
        cpu = psutil.cpu_percent(interval=None)
        root_drive = (os.path.splitdrive(os.getcwd())[0] + os.sep) if sys.platform == "win32" else '/'
        disk = psutil.disk_usage(root_drive)
        
        battery_pct = 100
        is_charging = False
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_pct = int(battery.percent)
                is_charging = battery.power_plugged
        except Exception:
            pass

        return web.json_response({
            "cpu_percent": round(cpu, 1),
            "ram_percent": round(mem.percent, 1),
            "ram_used_gb": round(mem.used / (1024**3), 1),
            "ram_total_gb": round(mem.total / (1024**3), 1),
            "battery_percent": battery_pct,
            "battery_charging": is_charging,
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "voice_state": self.voice_state,
            "wake_word_shield": Config.WAKE_WORD_REQUIRED,
            "presentation_mode": getattr(listener, "presentation_mode", False),
            "local_ip": self.local_ip,
            "port": self.port,
            "network_url": f"http://{self.local_ip}:{self.port}"
        })

    async def handle_history(self, request):
        return web.json_response({
            "messages": self.messages[-35:]
        })

    async def handle_command(self, request):
        data = await request.json()
        query = data.get("query", "").strip()
        if not query:
            return web.json_response({"response": ""})

        # Add user query to history
        self.add_message("user", query)
        self.voice_state = "processing"

        # Execute command in worker thread
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, brain.process, query)

        self.add_message("jarvis", response)
        self.voice_state = "speaking"

        # Speak response in background thread
        threading.Thread(target=self._speak_and_reset, args=(response,), daemon=True).start()

        return web.json_response({"response": response})

    def _speak_and_reset(self, text: str):
        try:
            speaker.speak(text)
        finally:
            self.voice_state = "standby"

    async def handle_manual_listen(self, request):
        """Allows clicking the microphone button or pressing Push-To-Talk hotkey to capture speech."""
        self.voice_state = "manual_listening"
        loop = asyncio.get_event_loop()
        
        try:
            raw_audio = await loop.run_in_executor(None, lambda: listener.listen(timeout=5, phrase_time_limit=8))
        except Exception:
            raw_audio = ""

        if not raw_audio:
            self.voice_state = "standby"
            return web.json_response({"command": "", "response": ""})

        # Check wake word or extract command
        has_wake, extracted = wake_detector.extract_command(raw_audio)
        command = extracted if has_wake and extracted else raw_audio

        self.add_message("user", command)
        self.voice_state = "processing"

        response = await loop.run_in_executor(None, brain.process, command)
        self.add_message("jarvis", response)
        self.voice_state = "speaking"

        threading.Thread(target=self._speak_and_reset, args=(response,), daemon=True).start()
        return web.json_response({"command": command, "response": response})

    def add_message(self, role: str, text: str):
        self.messages.append({
            "role": role,
            "text": text,
            "time": time.strftime("%H:%M:%S")
        })

    def start_voice_loop(self):
        """Background listener thread with Wake Word & Background Audio Filter."""
        def worker():
            from core.listener import PYAUDIO_AVAILABLE, SOUNDDEVICE_AVAILABLE
            if not PYAUDIO_AVAILABLE and not SOUNDDEVICE_AVAILABLE:
                print("[INFO] Microphone listener idle: No audio input drivers installed.")
                while self.running:
                    time.sleep(2.0)
                return

            listener.calibrate()
            
            while self.running:
                if self.voice_state in ["speaking", "processing", "manual_listening"]:
                    time.sleep(0.2)
                    continue

                if Config.WAKE_WORD_REQUIRED:
                    self.voice_state = "standby"
                    raw_audio = listener.listen(timeout=3.5, phrase_time_limit=8)
                    if not raw_audio:
                        time.sleep(0.1)
                        continue

                    has_wake, extracted_command = wake_detector.extract_command(raw_audio)
                    if not has_wake:
                        # Silently ignore stray background songs or chatter
                        time.sleep(0.1)
                        continue

                    # Wake word was detected!
                    if extracted_command:
                        command = extracted_command
                    else:
                        ack = wake_detector.get_acknowledgement(raw_audio)
                        self.add_message("jarvis", ack)
                        self.voice_state = "speaking"
                        speaker.speak(ack)

                        self.voice_state = "listening"
                        followup = listener.listen(timeout=5, phrase_time_limit=8)
                        if not followup:
                            self.voice_state = "standby"
                            continue
                        _, clean_followup = wake_detector.extract_command(followup)
                        command = clean_followup if clean_followup else followup

                    # Execute command
                    self.add_message("user", command)
                    self.voice_state = "processing"
                    response = brain.process(command)
                    self.add_message("jarvis", response)

                    self.voice_state = "speaking"
                    speaker.speak(response)
                    self.voice_state = "standby"
                else:
                    raw_audio = listener.listen()
                    if raw_audio:
                        self.add_message("user", raw_audio)
                        self.voice_state = "processing"
                        response = brain.process(raw_audio)
                        self.add_message("jarvis", response)
                        self.voice_state = "speaking"
                        speaker.speak(response)
                        self.voice_state = "standby"
                    time.sleep(0.2)

        self.voice_thread = threading.Thread(target=worker, daemon=True)
        self.voice_thread.start()

    def launch_window(self):
        """Opens UI in the user's default browser or preferred browser without breaking on missing apps."""
        url = f"http://127.0.0.1:{self.port}"
        
        # 1. Standard python webbrowser module (opens user's active default browser on any OS)
        try:
            opened = webbrowser.open(url)
            if opened:
                return
        except Exception:
            pass

        # 2. Platform-specific fallback
        if sys.platform == "darwin":  # macOS
            try:
                subprocess.Popen(["open", url])
            except Exception:
                pass
        elif sys.platform == "win32":  # Windows
            try:
                os.startfile(url)
            except Exception:
                pass
        else:  # Linux
            try:
                subprocess.Popen(["xdg-open", url])
            except Exception:
                pass

    def run(self):
        """Starts web server accessible locally and across all devices on the same network."""
        self.local_ip = get_local_ip()

        # 1. Launch background voice loop
        self.start_voice_loop()

        # 2. Delayed browser window open
        threading.Timer(0.8, self.launch_window).start()

        # 3. Print clean network connection guide
        print(f"\n==================================================")
        print(f"⚡ J.A.R.V.I.S. TACTICAL OS ONLINE")
        print(f"🖥️  Local Device:   http://localhost:{self.port}")
        if self.local_ip and self.local_ip != "127.0.0.1":
            print(f"📱 Remote Devices: http://{self.local_ip}:{self.port} (Access from Mobile/Tablet on same Wi-Fi)")
        print(f"⚡ Press Ctrl+C to terminate")
        print(f"==================================================\n")

        # 4. Run aiohttp server bound to 0.0.0.0 for cross-device support
        web.run_app(self.app, host="0.0.0.0", port=self.port, print=None)

server = JarvisServer(port=8888)

if __name__ == "__main__":
    server.run()
