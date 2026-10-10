import os
import sys
import ctypes
import tempfile
import time
import subprocess
import threading
import speech_recognition as sr

IS_WINDOWS = sys.platform == "win32"
WINMM_AVAILABLE = False
if IS_WINDOWS:
    try:
        _w = ctypes.windll.winmm
        WINMM_AVAILABLE = True
    except Exception:
        WINMM_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except Exception:
    pyaudio = None
    PYAUDIO_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except Exception:
    sd = None
    SOUNDDEVICE_AVAILABLE = False

MIC_DRIVER_AVAILABLE = PYAUDIO_AVAILABLE or SOUNDDEVICE_AVAILABLE or (IS_WINDOWS and WINMM_AVAILABLE)

from core.config import Config

class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.lock = threading.Lock()
        
        # Acoustic Tuning
        self.recognizer.energy_threshold = int(getattr(Config, "MIC_ENERGY_THRESHOLD", 120))
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.3
        self.recognizer.pause_threshold = 0.65
        self.recognizer.phrase_threshold = 0.20
        self.recognizer.non_speaking_duration = 0.40
        
        self.language = Config.SPEECH_LANG
        self.calibrated = False
        self.presentation_mode = False
        self.device_index = self._determine_device_index()

    def set_presentation_mode(self, enabled: bool):
        """Toggles presentation/call mode: locks high sensitivity and prevents threshold inflation from call audio."""
        self.presentation_mode = enabled
        if enabled:
            self.recognizer.energy_threshold = 110
            self.recognizer.dynamic_energy_threshold = False
            self.recognizer.pause_threshold = 0.75
            self.recognizer.phrase_threshold = 0.18
        else:
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.70
            self.recognizer.phrase_threshold = 0.20
            self.recognizer.energy_threshold = 140

    def _determine_device_index(self):
        """Finds the best hardware microphone device index across macOS and Windows."""
        if Config.MIC_DEVICE_INDEX and str(Config.MIC_DEVICE_INDEX).strip().isdigit():
            return int(Config.MIC_DEVICE_INDEX)

        # On Windows, None is the gold standard because it routes to Windows Default Audio Endpoint (WASAPI/MME)
        if IS_WINDOWS:
            return None

        if not PYAUDIO_AVAILABLE:
            return 0

        # PyAudio device scan on macOS
        p = pyaudio.PyAudio()
        best_index = None
        builtin_index = None
        
        try:
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
        if not PYAUDIO_AVAILABLE:
            self.calibrated = bool(SOUNDDEVICE_AVAILABLE or (IS_WINDOWS and WINMM_AVAILABLE))
            return
        try:
            with self.lock:
                eff_idx = None if (IS_WINDOWS and not Config.MIC_DEVICE_INDEX) else self.device_index
                with sr.Microphone(device_index=eff_idx) as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    if IS_WINDOWS:
                        # Windows microphones often have lower preamp levels, clamp floor to 30
                        self.recognizer.energy_threshold = max(30, min(self.recognizer.energy_threshold, 220))
                    else:
                        self.recognizer.energy_threshold = max(70, min(self.recognizer.energy_threshold, 190))
                    self.calibrated = True
        except Exception:
            self.calibrated = True

    def _listen_sounddevice(self, phrase_time_limit=None, status_callback=None) -> str:
        """Records microphone input via sounddevice when PyAudio is not available."""
        try:
            sample_rate = 16000
            duration = float(phrase_time_limit) if phrase_time_limit is not None else 4.0
            if status_callback:
                status_callback("Listening...")
            recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
            sd.wait()
            if status_callback:
                status_callback("Processing speech...")
            audio_bytes = recording.tobytes()
            audio_data = sr.AudioData(audio_bytes, sample_rate, 2)
            
            for lang in [self.language, "hi-IN", "en-US"]:
                try:
                    text = self.recognizer.recognize_google(audio_data, language=lang)
                    if text:
                        return text.strip()
                except Exception:
                    continue
            return ""
        except Exception:
            return ""

    def _listen_winmm(self, timeout=None, phrase_time_limit=None, status_callback=None) -> str:
        """Records microphone input natively on Windows using winmm.dll (zero external dependencies)."""
        temp_wav = os.path.join(tempfile.gettempdir(), f"jarvis_rec_{os.getpid()}_{int(time.time()*1000)}.wav")
        try:
            winmm = ctypes.windll.winmm
            winmm.mciSendStringW("close jarvis_rec", None, 0, None)
            res = winmm.mciSendStringW("open new type waveaudio alias jarvis_rec", None, 0, None)
            if res != 0:
                return ""
            winmm.mciSendStringW("set jarvis_rec samplespersec 16000 bitspersample 16 channels 1", None, 0, None)
            res = winmm.mciSendStringW("record jarvis_rec", None, 0, None)
            if res != 0:
                winmm.mciSendStringW("close jarvis_rec", None, 0, None)
                return ""

            if status_callback:
                status_callback("Listening...")

            duration = float(phrase_time_limit) if phrase_time_limit is not None else 4.0
            time.sleep(duration)

            winmm.mciSendStringW(f'save jarvis_rec "{temp_wav}"', None, 0, None)
            winmm.mciSendStringW("close jarvis_rec", None, 0, None)

            if not os.path.exists(temp_wav) or os.path.getsize(temp_wav) < 100:
                return ""

            if status_callback:
                status_callback("Processing speech...")

            with sr.AudioFile(temp_wav) as source:
                audio_data = self.recognizer.record(source)

            for lang in [self.language, "hi-IN", "en-US"]:
                try:
                    text = self.recognizer.recognize_google(audio_data, language=lang)
                    if text:
                        return text.strip()
                except Exception:
                    continue
            return ""
        except Exception:
            return ""
        finally:
            if os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                except Exception:
                    pass

    def listen(self, timeout=None, phrase_time_limit=None, status_callback=None) -> str:
        """Listens from the microphone with clean acoustics, call resilience, and multi-tier Windows fallback."""
        eff_timeout = timeout if timeout is not None else Config.MIC_TIMEOUT
        eff_phrase_limit = phrase_time_limit if phrase_time_limit is not None else Config.MIC_PHRASE_LIMIT

        # Tier 1: Try PyAudio with SpeechRecognition if available
        if PYAUDIO_AVAILABLE:
            try:
                eff_idx = None if (IS_WINDOWS and not Config.MIC_DEVICE_INDEX) else self.device_index
                with self.lock:
                    with sr.Microphone(device_index=eff_idx) as source:
                        if self.presentation_mode:
                            self.recognizer.energy_threshold = 110
                            self.recognizer.dynamic_energy_threshold = False
                        else:
                            if IS_WINDOWS:
                                if self.recognizer.energy_threshold > 250:
                                    self.recognizer.energy_threshold = 150
                                elif self.recognizer.energy_threshold < 30:
                                    self.recognizer.energy_threshold = 45
                            else:
                                if self.recognizer.energy_threshold > 200:
                                    self.recognizer.energy_threshold = 150
                                elif self.recognizer.energy_threshold < 60:
                                    self.recognizer.energy_threshold = 80

                        if not self.calibrated:
                            if status_callback:
                                status_callback("Calibrating acoustic sensors...")
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                            if IS_WINDOWS:
                                self.recognizer.energy_threshold = max(30, min(self.recognizer.energy_threshold, 220))
                            else:
                                self.recognizer.energy_threshold = max(70, min(self.recognizer.energy_threshold, 190))
                            self.calibrated = True

                        if status_callback:
                            status_callback("Listening...")

                        audio = self.recognizer.listen(
                            source,
                            timeout=eff_timeout,
                            phrase_time_limit=eff_phrase_limit
                        )

                        if status_callback:
                            status_callback("Processing speech...")

                        text = ""
                        for lang in [self.language, "hi-IN", "en-US"]:
                            try:
                                text = self.recognizer.recognize_google(audio, language=lang)
                                if text:
                                    break
                            except Exception:
                                continue
                        return text.strip() if text else ""
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return ""
            except Exception:
                # If PyAudio hardware access fails, fall through to Tier 2/3
                pass

        # Tier 2: Try SoundDevice if available
        if SOUNDDEVICE_AVAILABLE:
            try:
                res = self._listen_sounddevice(phrase_time_limit=eff_phrase_limit, status_callback=status_callback)
                if res:
                    return res
            except Exception:
                pass

        # Tier 3: Try Windows Native winmm.dll (Zero dependency)
        if IS_WINDOWS and WINMM_AVAILABLE:
            try:
                res = self._listen_winmm(timeout=eff_timeout, phrase_time_limit=eff_phrase_limit, status_callback=status_callback)
                if res:
                    return res
            except Exception:
                pass

        if status_callback:
            status_callback("Microphone unavailable")
        return ""

listener = Listener()
