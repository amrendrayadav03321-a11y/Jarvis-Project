import os
import sys
import time
import psutil
import asyncio
import threading
import subprocess
from pathlib import Path
from aiohttp import web

from core.config import Config
from core.speaker import speaker
from core.listener import listener
from core.brain import brain
from core.wakeword import wake_detector

WEB_DIR = Path(__file__).resolve().parent / "web"

class JarvisServer:
    def __init__(self, port: int = 8888):
        self.port = port
        self.app = web.Application()
        self.messages = [
            {
                "role": "jarvis",
                "text": f"Jarvis tactical protocols online. Ready for your command, {Config.USER_NAME}.",
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
        self.app.router.add_post("/api/command", self.handle_command)
        self.app.router.add_post("/api/listen", self.handle_manual_listen)
        self.app.router.add_static("/", path=str(WEB_DIR), name="static")

    async def handle_index(self, request):
        return web.FileResponse(WEB_DIR / "index.html")

    async def handle_status(self, request):
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
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
            "wake_word_shield": Config.WAKE_WORD_REQUIRED
        })

    async def handle_history(self, request):
        return web.json_response({
            "messages": self.messages[-30:]
        })

    async def handle_command(self, request):
        data = await request.json()
        query = data.get("query", "").strip()
        if not query:
            return web.json_response({"response": ""})

        # Add user query to history
        self.add_message("user", query)
        self.voice_state = "processing"

        # Execute command in thread to avoid blocking event loop
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
        """Allows clicking the microphone button on the UI to capture speech."""
        self.voice_state = "listening"
        loop = asyncio.get_event_loop()
        
        raw_audio = await loop.run_in_executor(None, listener.listen)
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
            # Calibrate sensors once
            listener.calibrate()
            
            while self.running:
                if self.voice_state == "speaking":
                    time.sleep(0.3)
                    continue

                if Config.WAKE_WORD_REQUIRED:
                    self.voice_state = "standby"
                    raw_audio = listener.listen()
                    if not raw_audio:
                        time.sleep(0.1)
                        continue

                    has_wake, extracted_command = wake_detector.extract_command(raw_audio)
                    if not has_wake:
                        # FILTER BACKGROUND AUDIO / MUSIC!
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
                        followup = listener.listen()
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
        """Opens dedicated application window using Brave Browser, Chrome, or Safari."""
        url = f"http://127.0.0.1:{self.port}"
        
        # 1. Try Brave Browser in app mode (frameless desktop window)
        brave_path = Path("/Applications/Brave Browser.app")
        if brave_path.exists():
            try:
                subprocess.Popen(["open", "-na", "Brave Browser", "--args", f"--app={url}", "--window-size=1280,840"])
                return
            except Exception:
                pass

        # 2. Try Google Chrome in app mode
        chrome_path = Path("/Applications/Google Chrome.app")
        if chrome_path.exists():
            try:
                subprocess.Popen(["open", "-na", "Google Chrome", "--args", f"--app={url}", "--window-size=1280,840"])
                return
            except Exception:
                pass

        # 3. Fallback: default macOS open
        try:
            subprocess.Popen(["open", url])
        except Exception:
            pass

    def run(self):
        """Starts web server and background voice worker."""
        # 1. Launch background voice loop
        self.start_voice_loop()

        # 2. Delayed browser window open
        threading.Timer(0.8, self.launch_window).start()

        # 3. Run aiohttp server
        web.run_app(self.app, host="127.0.0.1", port=self.port, print=None)

server = JarvisServer(port=8888)

if __name__ == "__main__":
    server.run()
