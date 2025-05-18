from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import pyqtSlot

from services.speech_worker import SpeechWorker, LANGUAGE_CODE_MAP
from services.tts_engine import TTSEngine


class SpeechToSpeechPage(QWidget):
    def __init__(self, translator, main_window):
        super().__init__()
        self.translator = translator
        self.main_window = main_window
        self.from_lang = main_window.current_from_language
        self.to_lang = main_window.current_to_language

        self.listening = False
        self.worker = None
        self.last_translated_text = ""

        self.tts = TTSEngine()
        self.is_speaking = False

        # UI components
        self.listen_button = QPushButton("🎤 Start Listening")
        self.listen_button.clicked.connect(self.toggle_listening)

        self.recognized_text = QTextEdit()
        self.recognized_text.setReadOnly(True)
        self.recognized_text.setPlaceholderText("Recognized speech will appear here...")

        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        self.translated_text.setPlaceholderText("Translated speech will appear here and be spoken aloud...")

        self.speak_button = QPushButton("🔊 Speak")
        self.speak_button.clicked.connect(self.speak_last_translation)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.listen_button)
        layout.addWidget(self.recognized_text)
        layout.addWidget(self.translated_text)
        layout.addStretch()
        layout.addWidget(self.speak_button)
        self.setLayout(layout)

        # Language change handling
        self.main_window.languageChanged.connect(self.update_languages)

    def toggle_listening(self):
        if not self.listening:
            self.listen_button.setText("🛑 Stop Listening")
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        if self.worker is not None:
            return

        lang_code = LANGUAGE_CODE_MAP.get(self.from_lang, "en-US")
        mic_index = self.main_window.get_selected_input_device_index()
        if mic_index is None:
            self.recognized_text.append("[Error] No valid microphone selected.")
            self.stop_listening()
            return

        self.worker = SpeechWorker(lang_code, mic_index=mic_index)
        self.worker.result_ready.connect(self.handle_recognized_text)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start_listening()
        self.listening = True

    def stop_listening(self):
        if self.worker:
            self.worker.stop_listening()
            self.worker = None
        self.listening = False
        self.listen_button.setText("🎤 Start Listening")

    @pyqtSlot(str)
    def handle_recognized_text(self, text):
        self.recognized_text.append(text)
        translated = self.translator.translate(text, self.from_lang, self.to_lang)
        self.last_translated_text = translated
        self.translated_text.append(translated)
        self.play_audio(translated)

    @pyqtSlot(str)
    def handle_error(self, msg):
        self.recognized_text.append(f"[Error] {msg}")
        self.stop_listening()

    def speak_last_translation(self):
        if self.last_translated_text:
            self.play_audio(self.last_translated_text)

    def play_audio(self, text):
        self.is_speaking = True
        speaker_index = self.main_window.get_selected_output_device_index()
        if speaker_index is None:
            self.translated_text.append("[Error] No valid speaker selected.")
            return

        self.tts.set_output_device(speaker_index)
        self.tts.speak(text, self.to_lang)
        self.is_speaking = False

    @pyqtSlot(str, str)
    def update_languages(self, from_lang, to_lang):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.stop_listening()
        self.recognized_text.clear()
        self.translated_text.clear()
        self.last_translated_text = ""

    def reset(self):
        """Reset page state when switching from it."""
        self.stop_listening()
        self.recognized_text.clear()
        self.translated_text.clear()
        self.last_translated_text = ""