# services/speech_worker.py

from PyQt6.QtCore import QObject, pyqtSignal
import speech_recognition as sr
import threading

LANGUAGE_CODE_MAP = {
    "en": "en-US",
    "ar": "ar-SA",
    "ur": "ur-PK"
}


class SpeechWorker(QObject):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, lang_code="en-US", mic_index=None):
        super().__init__()
        self.lang_code = lang_code
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0
        self.recognizer.energy_threshold = 300
        self.mic_index = mic_index
        self.mic = None
        self.listening = False
        self._stop_event = threading.Event()

    def set_mic_index(self, index: int):
        self.mic_index = index

    def start_listening(self):
        if self.listening:
            return
        try:
            self.mic = sr.Microphone(device_index=self.mic_index)
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source)

            self._stop_event.clear()
            self.listening = True
            threading.Thread(target=self._listen_loop, daemon=True).start()
        except Exception as e:
            self.error_occurred.emit(f"Mic Init Error: {str(e)}")

    def stop_listening(self):
        self._stop_event.set()
        self.listening = False

    def _listen_loop(self):
        while not self._stop_event.is_set():
            try:
                with self.mic as source:
                    audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language=self.lang_code)
                self.result_ready.emit(text)
            except sr.WaitTimeoutError:
                # No speech within timeout — loop to try again
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                self.error_occurred.emit("Network error: " + str(e))
            except Exception as e:
                self.error_occurred.emit("Microphone error: " + str(e)) 