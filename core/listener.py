import os
import subprocess
import speech_recognition as sr
import pyaudio
from core.config import Config

class AudioChimes:
    """Plays non-blocking native macOS sound effects."""
    @staticmethod
    def play(sound_name: str):
        if not Config.AUDIO_CHIMES:
            return
        sound_path = f"/System/Library/Sounds/{sound_name}.aiff"
        if os.path.exists(sound_path):
            try:
                subprocess.Popen(["afplay", sound_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Optimized acoustic thresholds for natural conversation
        self.recognizer.energy_threshold = Config.MIC_ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 1.1        # Prevents premature cut-offs
        self.recognizer.phrase_threshold = 0.25      # Starts capturing quickly
        self.recognizer.non_speaking_duration = 0.6
        
        self.language = Config.SPEECH_LANG
        self.calibrated = False
        self.device_index = self._determine_device_index()

    def _determine_device_index(self) -> int:
        """Finds the best hardware microphone device index on macOS."""
        if Config.MIC_DEVICE_INDEX and str(Config.MIC_DEVICE_INDEX).strip().isdigit():
            return int(Config.MIC_DEVICE_INDEX)

        # PyAudio device scan
        p = pyaudio.PyAudio()
        best_index = None
        builtin_index = None
        
        try:
            device_count = p.get_device_count()
            for i in range(device_count):
                dev_info = p.get_device_info_by_index(i)
                name = dev_info.get("name", "")
                max_inputs = dev_info.get("maxInputChannels", 0)
                
                if max_inputs > 0:
                    # Prefer Built-in / MacBook Air Microphone
                    if any(k in name.lower() for k in ["macbook", "built-in", "internal microphone"]):
                        builtin_index = i
                        break
                    elif best_index is None:
                        best_index = i
                        
            # Also check system default input
            try:
                default_info = p.get_default_input_device_info()
                default_idx = default_info.get("index")
            except Exception:
                default_idx = 0
                
            selected = builtin_index if builtin_index is not None else (best_index if best_index is not None else default_idx)
            return selected
        except Exception:
            return 0
        finally:
            p.terminate()

    def calibrate(self):
        """Calibrates microphone for ambient noise with safety clamps."""
        try:
            with sr.Microphone(device_index=self.device_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                # Safeguard: clamp energy threshold between 80 and 450
                # Never let it become too deaf (500+) or hypersensitive (<70)
                self.recognizer.energy_threshold = max(80, min(self.recognizer.energy_threshold, 450))
                self.calibrated = True
        except Exception:
            self.calibrated = False

    def listen(self, status_callback=None) -> str:
        """Listens from the microphone and returns recognized text."""
        try:
            with sr.Microphone(device_index=self.device_index) as source:
                if not self.calibrated:
                    if status_callback:
                        status_callback("Calibrating acoustic sensors...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                    self.recognizer.energy_threshold = max(80, min(self.recognizer.energy_threshold, 450))
                    self.calibrated = True
                
                # Audio chime to let user know Jarvis is listening right now
                AudioChimes.play("Tink")
                
                if status_callback:
                    status_callback("Listening...")
                
                audio = self.recognizer.listen(
                    source,
                    timeout=Config.MIC_TIMEOUT,
                    phrase_time_limit=Config.MIC_PHRASE_LIMIT
                )
                
                # Chime confirming speech audio has been captured
                AudioChimes.play("Pop")
                
                if status_callback:
                    status_callback("Processing speech...")
                
                # Multi-lingual Speech-to-Text with Hindi/English fallback
                try:
                    text = self.recognizer.recognize_google(audio, language=self.language)
                except sr.UnknownValueError:
                    # Fallback to Hindi if primary was English, or vice-versa
                    fallback_lang = "hi-IN" if self.language != "hi-IN" else "en-IN"
                    text = self.recognizer.recognize_google(audio, language=fallback_lang)
                        
                return text.strip()

        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            if status_callback:
                status_callback(f"Acoustic Notice: {str(e)[:40]}")
            return ""

listener = Listener()
