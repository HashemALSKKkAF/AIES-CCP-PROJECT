from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import QTimer, pyqtSlot

from services.tts_engine import TTSEngine


class TextToSpeechPage(QWidget):
    def __init__(self, translator, main_window):
        super().__init__()
        self.translator = translator
        self.main_window = main_window
        self.from_lang = main_window.current_from_language
        self.to_lang = main_window.current_to_language

        self.main_window.languageChanged.connect(self.update_languages)

        self.input_text = QTextEdit(placeholderText="Enter text here...")
        self.input_text.textChanged.connect(self.on_text_changed)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        self.speaker_button = QPushButton("🔊 Speak")
        self.speaker_button.clicked.connect(self.force_speak)

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.speaker_button)

        layout.addWidget(self.input_text)
        layout.addWidget(self.output_text)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.typing_timer = QTimer(self)
        self.typing_timer.setInterval(5000)
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self.speak_translated_text)

        self.tts = TTSEngine()
        self.is_speaking = False

    def on_text_changed(self):
        self.typing_timer.start()
        if self.is_speaking:
            self.pause_speaking()

    def translate_text(self):
        user_text = self.input_text.toPlainText().strip()
        if not user_text:
            self.output_text.clear()
            return ""
        translated = self.translator.translate(user_text, self.from_lang, self.to_lang)
        self.output_text.setText(translated)
        return translated

    def speak_translated_text(self):
        translated_text = self.translate_text()
        if translated_text:
            self.play_audio(translated_text)

    def force_speak(self):
        self.typing_timer.stop()
        self.speak_translated_text()

    def pause_speaking(self):
        self.tts.stop()
        self.is_speaking = False

    def play_audio(self, text):
        self.is_speaking = True
        output_index = self.main_window.get_selected_output_device_index()
        self.tts.set_output_device(output_index)
        self.tts.speak(text, self.to_lang)
        self.is_speaking = False

    @pyqtSlot(str, str)
    def update_languages(self, from_lang, to_lang):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.force_speak() 