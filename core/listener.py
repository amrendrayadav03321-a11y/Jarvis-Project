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
        
        # High-Speed Acoustic Tuning: Ultra-fast speech capture and low latency
        self.recognizer.energy_threshold = int(getattr(Config, "MIC_ENERGY_THRESHOLD", 80))
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.10
        self.recognizer.dynamic_energy_ratio = 1.25
        self.recognizer.pause_threshold = 0.55        # Sub-second pause detection (ultra-fast response)
        self.recognizer.phrase_threshold = 0.12       # Instantly triggers upon first spoken syllable
        self.recognizer.non_speaking_duration = 0.35  # Cuts trailing silence rapidly
        
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
                    # Prefer Built-in / MacBook Air Microphone array
                    if any(k in name.lower() for k in ["macbook", "built-in", "internal microphone"]):
                        builtin_index = i
                        break
                    elif best_index is None:
                        best_index = i
                        
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
        """Calibrates microphone with high-sensitivity floor and safety clamps."""
        try:
            with sr.Microphone(device_index=self.device_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                # High sensitivity clamp: 30 to 220
                # Ensures soft speech is never dropped, while loud noise doesn't permanently deafen mic
                self.recognizer.energy_threshold = max(30, min(self.recognizer.energy_threshold, 220))
                self.calibrated = True
        except Exception:
            self.calibrated = False

    def listen(self, status_callback=None) -> str:
        """Listens from the microphone with sub-second turnaround time."""
        try:
            with sr.Microphone(device_index=self.device_index) as source:
                if not self.calibrated:
                    if status_callback:
                        status_callback("Calibrating acoustic sensors...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    self.recognizer.energy_threshold = max(30, min(self.recognizer.energy_threshold, 220))
                    self.calibrated = True
                
                # Audio chime: ready to listen
                AudioChimes.play("Tink")
                
                if status_callback:
                    status_callback("Listening...")
                
                audio = self.recognizer.listen(
                    source,
                    timeout=Config.MIC_TIMEOUT,
                    phrase_time_limit=Config.MIC_PHRASE_LIMIT
                )
                
                # Audio chime: audio captured
                AudioChimes.play("Pop")
                
                if status_callback:
                    status_callback("Processing speech...")
                
                # Rapid multi-lingual transcription with fast fallback
                text = ""
                try:
                    text = self.recognizer.recognize_google(audio, language=self.language)
                except sr.UnknownValueError:
                    fallback_lang = "hi-IN" if self.language != "hi-IN" else "en-IN"
                    try:
                        text = self.recognizer.recognize_google(audio, language=fallback_lang)
                    except Exception:
                        return ""
                except Exception:
                    return ""
                        
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
