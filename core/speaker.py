import os
import re
import sys
import asyncio
import subprocess
import tempfile
from pathlib import Path
from core.config import Config

class Speaker:
    def __init__(self):
        self.engine = Config.TTS_ENGINE
        self.default_macos_voice = Config.MACOS_VOICE
        self.hindi_macos_voice = Config.MACOS_HINDI_VOICE
        self.hinglish_macos_voice = Config.MACOS_HINGLISH_VOICE
        self.macos_rate = Config.MACOS_RATE
        
        self.default_edge_voice = Config.EDGE_VOICE
        self.hindi_edge_voice = Config.EDGE_HINDI_VOICE
        self.edge_pitch = Config.EDGE_PITCH
        self.edge_rate = Config.EDGE_RATE

    def _clean_text_for_speech(self, text: str) -> str:
        """Removes markdown symbols, URLs, and noisy emojis for clean speech output."""
        cleaned = re.sub(r'[\*_`#>\-\[\]]', ' ', text)
        cleaned = re.sub(r'https?://\S+|www\.\S+', 'a web link', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _is_hindi(self, text: str) -> tuple[bool, str]:
        """Detects if text contains Devanagari Hindi or Hinglish.
        Returns (is_hindi, script_type: 'devanagari' | 'hinglish' | 'english')
        """
        # Check Devanagari script (Unicode range 0900-097F)
        if re.search(r'[\u0900-\u097F]', text):
            return True, "devanagari"
            
        # Check common Hinglish markers
        hinglish_markers = [
            "karo", "khol", "chala", "diya", "karte", "raha", "hoon", "aapka",
            "shukriya", "namaste", "dhanyawad", "kaise", "kya", "hai", "baje",
            "gaana", "sunao", "kijiye", "batao", "chalaye", "rahe", "suno"
        ]
        words = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
        if any(marker in words for marker in hinglish_markers):
            return True, "hinglish"
            
        return False, "english"

    def _play_audio_file(self, file_path: Path) -> bool:
        """Plays an audio file cross-platform on macOS, Windows, and Linux."""
        if sys.platform == "darwin":
            try:
                subprocess.run(
                    ["afplay", str(file_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
                return True
            except Exception:
                return False
        elif sys.platform == "win32":
            try:
                # Use Windows Media Player COM object via PowerShell (native on Windows 10/11)
                safe_path = str(file_path).replace("'", "''")
                ps_script = (
                    f"$w = New-Object -ComObject WMPlayer.OCX; "
                    f"$w.settings.volume = 100; "
                    f"$w.URL = '{safe_path}'; "
                    f"$w.controls.play(); "
                    f"Start-Sleep -Milliseconds 100; "
                    f"while ($w.playState -eq 3 -or $w.playState -eq 9 -or $w.playState -eq 0 -or $w.playState -eq 6) {{ "
                    f"    Start-Sleep -Milliseconds 50; "
                    f"}}"
                )
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
                return True
            except Exception:
                return False
        else:
            for player in [["mpv", str(file_path)], ["ffplay", "-nodisp", "-autoexit", str(file_path)], ["aplay", str(file_path)]]:
                try:
                    subprocess.run(player, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    return True
                except Exception:
                    continue
            return False

    def speak(self, text: str) -> None:
        """Speaks the text using Edge Neural TTS or OS native speech fallback."""
        if not text or not text.strip():
            return
            
        clean_text = self._clean_text_for_speech(text)
        is_hindi, script_type = self._is_hindi(clean_text)
        
        # Pick appropriate male voice
        if is_hindi:
            edge_voice = self.hindi_edge_voice  # 'hi-IN-MadhurNeural' (Male)
            macos_voice = self.hindi_macos_voice  # 'Rishi' (Male)
        else:
            edge_voice = self.default_edge_voice  # 'en-GB-RyanNeural' (Male)
            macos_voice = self.default_macos_voice  # 'Daniel' (Male)

        # Try Edge-TTS first if configured
        if self.engine == "edge":
            success = self._speak_edge(clean_text, edge_voice)
            if success:
                return

        # Fallback to platform-native offline TTS
        if sys.platform == "win32":
            self._speak_windows(clean_text)
        elif sys.platform == "darwin":
            self._speak_macos(clean_text, macos_voice)
        else:
            try:
                subprocess.run(["espeak", clean_text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    def _speak_macos(self, text: str, voice: str) -> bool:
        """Uses macOS native say command with chosen male voice and deep cadence."""
        try:
            cmd = ["say"]
            if voice:
                cmd.extend(["-v", voice])
            if self.macos_rate:
                cmd.extend(["-r", str(self.macos_rate)])
            cmd.append(text)
            subprocess.run(cmd, check=True)
            return True
        except Exception:
            try:
                # Fallback: say without specifying voice
                fallback_cmd = ["say"]
                if self.macos_rate:
                    fallback_cmd.extend(["-r", str(self.macos_rate)])
                fallback_cmd.append(text)
                subprocess.run(fallback_cmd, check=True)
                return True
            except Exception:
                return False

    def _speak_windows(self, text: str) -> bool:
        """Uses Windows native SAPI SpeechSynthesizer via PowerShell with zero external dependencies."""
        try:
            escaped = text.replace("'", "''").replace('"', '`"')
            ps_script = (
                "Add-Type -AssemblyName System.Speech; "
                "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$synth.Rate = 0; "
                f"$synth.Speak('{escaped}');"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except Exception:
            return False

    def _speak_edge(self, text: str, voice: str) -> bool:
        """Uses Microsoft Edge Neural TTS with customized pitch for deep male voice."""
        try:
            import edge_tts
            temp_file = Path(tempfile.gettempdir()) / "jarvis_speech.mp3"
            
            async def generate_audio():
                communicate = edge_tts.Communicate(
                    text,
                    voice,
                    pitch=self.edge_pitch,
                    rate=self.edge_rate
                )
                await communicate.save(str(temp_file))
                
            async def run_with_timeout():
                await asyncio.wait_for(generate_audio(), timeout=1.8)

            asyncio.run(run_with_timeout())
            
            if temp_file.exists() and temp_file.stat().st_size > 0:
                self._play_audio_file(temp_file)
                temp_file.unlink(missing_ok=True)
                return True
            return False
        except Exception:
            return False

# Global speaker instance
speaker = Speaker()
