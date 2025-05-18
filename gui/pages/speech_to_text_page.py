from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import pyqtSlot

from services.speech_worker import SpeechWorker, LANGUAGE_CODE_MAP


class SpeechToTextPage(QWidget):
    def __init__(self, translator, main_window):
        super().__init__()
        self.translator = translator
        self.main_window = main_window
        self.from_lang = main_window.current_from_language
        self.to_lang = main_window.current_to_language

        self.layout = QVBoxLayout()
        self.start_button = QPushButton("🎤 Start Listening")
        self.start_button.clicked.connect(self.toggle_listening)

        self.recognized_text = QTextEdit()
        self.recognized_text.setReadOnly(True)
        self.recognized_text.setPlaceholderText("Recognized speech will appear here...")

        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        self.translated_text.setPlaceholderText("Translated text will appear here...")

        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.recognized_text)
        self.layout.addWidget(self.translated_text)
        self.setLayout(self.layout)

        self.worker = None
        self.listening = False

        self.main_window.languageChanged.connect(self.update_languages)

    def toggle_listening(self):
        if not self.listening:
            self.start_button.setText("🛑 Stop Listening")
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        if self.worker is not None:
            return  # Prevent duplicate listeners

        lang_code = LANGUAGE_CODE_MAP.get(self.from_lang, "en-US")
        mic_index = self.main_window.get_selected_input_device_index()
        if mic_index is None:
            self.recognized_text.append("[Error] No valid microphone selected.")
            self.stop_listening()
            return

        self.worker = SpeechWorker(lang_code, mic_index=mic_index)
        self.worker.result_ready.connect(self.display_text)
        self.worker.error_occurred.connect(self.display_error)
        self.worker.start_listening()
        self.listening = True

    def stop_listening(self):
        if self.worker:
            self.worker.stop_listening()
            self.worker = None
        self.listening = False
        self.start_button.setText("🎤 Start Listening")

    @pyqtSlot(str)
    def display_text(self, text):
        self.recognized_text.append(text)
        translated = self.translator.translate(text, self.from_lang, self.to_lang)
        self.translated_text.append(translated)

    @pyqtSlot(str)
    def display_error(self, msg):
        self.recognized_text.append(f"[Error] {msg}")
        self.stop_listening()

    @pyqtSlot(str, str)
    def update_languages(self, from_lang, to_lang):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.stop_listening()
        self.recognized_text.clear()
        self.translated_text.clear()

    def reset(self):
        """Reset the UI state, used when switching pages."""
        self.stop_listening()
        self.recognized_text.clear()
        self.translated_text.clear() 