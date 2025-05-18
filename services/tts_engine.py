# services/tts_engine.py

import os
import socket
import time
from gtts import gTTS
import pyttsx3
import pygame
import sounddevice as sd

SUPPORTED_LANGUAGES = {
    "en": "english",
    "ar": "arabic",
    "ur": "urdu"
}


class TTSEngine:
    """
    TTSEngine: A flexible Text-to-Speech (TTS) engine supporting both online (gTTS) and offline (pyttsx3) synthesis.
    This class provides a unified interface for converting text to speech, automatically selecting between Google Text-to-Speech (gTTS) when internet connectivity is available, and falling back to the offline pyttsx3 engine otherwise. It supports playback through selectable audio output devices and includes utility methods for safe file deletion and device management.
    Attributes:
        engine (pyttsx3.Engine): The offline TTS engine instance.
        output_device_index (int or None): Index of the selected audio output device for playback.
    Methods:
        set_output_device(index): Set the output device index for audio playback.
        is_connected(timeout): Check for internet connectivity.
        safe_delete(file_path, retries, delay): Safely delete a file with retries.
        play_audio(file_path): Play an audio file through the selected output device.
        get_device_name(): Get the name of the selected output device.
        speak(text, lang_code): Convert text to speech and play it, using gTTS if online, otherwise pyttsx3.
    """
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        self.engine.setProperty("volume", 1.0)
        self.output_device_index = None  # ⬅️ NEW

    def set_output_device(self, index: int):
        """Set the selected output device index for playback (used for gTTS only)."""
        self.output_device_index = index

    def is_connected(self, timeout=2):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except OSError:
            return False

    def safe_delete(self, file_path, retries=5, delay=0.3):
        for _ in range(retries):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return
            except PermissionError:
                time.sleep(delay)
        print(f"⚠️ Could not delete file: {file_path}")

    def play_audio(self, file_path):
        try:
            pygame.mixer.quit()
            pygame.mixer.init(devicename=self.get_device_name())
        except Exception as e:
            print(f"⚠️ Failed to init pygame mixer with output device: {e}")
            pygame.mixer.init()  # fallback
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()

    def get_device_name(self):
        """Returns device name for selected output index, used in pygame."""
        if self.output_device_index is None:
            return None
        try:
            device = sd.query_devices(self.output_device_index)
            return device['name']
        except Exception as e:
            print(f"⚠️ Failed to get speaker name: {e}")
            return None

    def speak(self, text, lang_code):
        if self.is_connected():
            try:
                print("🌐 Using gTTS (online)...")
                project_root = os.path.dirname(os.path.abspath(__file__))
                data_dir = os.path.join(project_root, "data")
                os.makedirs(data_dir, exist_ok=True)

                mp3_path = os.path.join(data_dir, "gtts_output.mp3")

                tts = gTTS(text=text, lang=lang_code)
                tts.save(mp3_path)

                self.play_audio(mp3_path)
                self.safe_delete(mp3_path)
                return
            except Exception as e:
                print(f"❌ gTTS failed or playback error: {e}")

        print("📴 Falling back to offline pyttsx3...")
        try:
            if getattr(self.engine, "_inLoop", False):
                self.engine.endLoop()
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"❌ pyttsx3 failed: {e}")