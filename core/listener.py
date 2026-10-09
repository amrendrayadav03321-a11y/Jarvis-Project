import os
import subprocess
import threading
import speech_recognition as sr
import pyaudio
from core.config import Config

class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.lock = threading.Lock()
        
        # Human-Centric Acoustic Tuning:
        # Prevents premature cut-offs while maintaining fast turnaround
        self.recognizer.energy_threshold = int(getattr(Config, "MIC_ENERGY_THRESHOLD", 120))
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.3
        self.recognizer.pause_threshold = 0.65        # Fast human pause turnaround (sub-second command finalization)
        self.recognizer.phrase_threshold = 0.20       # Fast syllable trigger
        self.recognizer.non_speaking_duration = 0.40  # Cuts trailing silence rapidly
        
        self.language = Config.SPEECH_LANG
        self.calibrated = False
        self.presentation_mode = False
        self.device_index = self._determine_device_index()

    def set_presentation_mode(self, enabled: bool):
        """Toggles presentation/call mode: locks high sensitivity and prevents threshold inflation from call audio."""
        self.presentation_mode = enabled
        if enabled:
            # Locked near-field sensitivity: guarantees capture even when call audio is playing
            self.recognizer.energy_threshold = 110
            self.recognizer.dynamic_energy_threshold = False
            self.recognizer.pause_threshold = 0.75
            self.recognizer.phrase_threshold = 0.18
        else:
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.70
            self.recognizer.phrase_threshold = 0.20
            self.recognizer.energy_threshold = 140

    def _determine_device_index(self) -> int:
        """Finds the best hardware microphone device index across macOS and Windows."""
        if Config.MIC_DEVICE_INDEX and str(Config.MIC_DEVICE_INDEX).strip().isdigit():
            return int(Config.MIC_DEVICE_INDEX)

        # PyAudio device scan
        p = pyaudio.PyAudio()
        best_index = None
        builtin_index = None
        
        try:
            # 1. Try system default input device first
            default_idx = None
            try:
                default_info = p.get_default_input_device_info()
                default_idx = default_info.get("index")
            except Exception:
                default_idx = None

            device_count = p.get_device_count()
            for i in range(device_count):
                dev_info = p.get_device_info_by_index(i)
                name = dev_info.get("name", "").lower()
                max_inputs = dev_info.get("maxInputChannels", 0)
                
                if max_inputs > 0:
                    # Windows & macOS built-in mic keywords
                    if any(k in name for k in ["macbook", "built-in", "internal microphone", "microphone array", "realtek", "high definition audio"]):
                        builtin_index = i
                        break
                    elif best_index is None:
                        best_index = i
                        
            if default_idx is not None:
                return default_idx
            if builtin_index is not None:
                return builtin_index
            if best_index is not None:
                return best_index
            return 0
        except Exception:
            return 0
        finally:
            try:
                p.terminate()
            except Exception:
                pass

    def calibrate(self):
        """Calibrates microphone with high-sensitivity floor and safety clamps."""
        try:
            with self.lock:
                with sr.Microphone(device_index=self.device_index) as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    # Clamping: 70 to 190
                    # Ensures soft speech is never dropped, while call noise doesn't permanently deafen mic
                    self.recognizer.energy_threshold = max(70, min(self.recognizer.energy_threshold, 190))
                    self.calibrated = True
        except Exception:
            self.calibrated = False

    def listen(self, timeout=None, phrase_time_limit=None, status_callback=None) -> str:
        """Listens from the microphone with clean acoustics, call resilience, and zero speaker feedback."""
        with self.lock:
            try:
                with sr.Microphone(device_index=self.device_index) as source:
                    # Presentation / Call Anti-Deafness Clamping:
                    # During conference calls (Zoom, Meet, Teams), other voices from speakers
                    # can cause dynamic_energy_threshold to drift into thousands (>1500).
                    # Clamping prevents the microphone from becoming deaf to the user.
                    if self.presentation_mode:
                        self.recognizer.energy_threshold = 110
                        self.recognizer.dynamic_energy_threshold = False
                    else:
                        if self.recognizer.energy_threshold > 200:
                            self.recognizer.energy_threshold = 150
                        elif self.recognizer.energy_threshold < 60:
                            self.recognizer.energy_threshold = 80

                    if not self.calibrated:
                        if status_callback:
                            status_callback("Calibrating acoustic sensors...")
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        self.recognizer.energy_threshold = max(70, min(self.recognizer.energy_threshold, 190))
                        self.calibrated = True
                    
                    if status_callback:
                        status_callback("Listening...")
                    
                    eff_timeout = timeout if timeout is not None else Config.MIC_TIMEOUT
                    eff_phrase_limit = phrase_time_limit if phrase_time_limit is not None else Config.MIC_PHRASE_LIMIT

                    audio = self.recognizer.listen(
                        source,
                        timeout=eff_timeout,
                        phrase_time_limit=eff_phrase_limit
                    )
                    
                    if status_callback:
                        status_callback("Processing speech...")
                    
                    # Multi-lingual transcription with fast fallback
                    text = ""
                    # 1. Try Indian English / Hinglish (en-IN)
                    try:
                        text = self.recognizer.recognize_google(audio, language=self.language)
                    except Exception:
                        pass

                    # 2. Try Hindi (hi-IN) if en-IN failed
                    if not text:
                        try:
                            text = self.recognizer.recognize_google(audio, language="hi-IN")
                        except Exception:
                            pass

                    # 3. Try Standard English (en-US) as fallback for clear technical commands
                    if not text:
                        try:
                            text = self.recognizer.recognize_google(audio, language="en-US")
                        except Exception:
                            pass
                            
                    return text.strip() if text else ""

            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except Exception as e:
                if status_callback:
                    status_callback(f"Acoustic Notice: {str(e)[:40]}")
                return ""

listener = Listener()
