from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSlot, QTimer


class TextToTextPage(QWidget):
    def __init__(self, translator, main_window):
        super().__init__()
        self.translator = translator
        self.main_window = main_window
        self.from_lang = main_window.current_from_language
        self.to_lang = main_window.current_to_language

        self.last_text = ""
        self.translation_delay_ms = 2000  # 2 seconds

        self.main_window.languageChanged.connect(self.update_languages)

        self.input_text = QTextEdit(placeholderText="Enter text here...")
        self.input_text.textChanged.connect(self.on_text_changed)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        self.translate_button = QPushButton("Translate")
        self.translate_button.clicked.connect(self.manual_translate)

        layout = QVBoxLayout()
        layout.addWidget(self.input_text)
        layout.addWidget(self.output_text)
        layout.addWidget(self.translate_button)
        self.setLayout(layout)

        self.translation_timer = QTimer(self)
        self.translation_timer.setInterval(self.translation_delay_ms)
        self.translation_timer.setSingleShot(True)
        self.translation_timer.timeout.connect(self.auto_translate)

    def on_text_changed(self):
        self.translation_timer.start()

    def auto_translate(self):
        current_text = self.input_text.toPlainText().strip()
        if current_text and current_text != self.last_text:
            self.translate_text(current_text)

    def manual_translate(self):
        text = self.input_text.toPlainText().strip()
        if text:
            self.translate_text(text)

    def translate_text(self, text):
        translated = self.translator.translate(text, self.from_lang, self.to_lang)
        self.output_text.setText(translated)
        self.last_text = text

    @pyqtSlot(str, str)
    def update_languages(self, from_lang, to_lang):
        self.from_lang = from_lang
        self.to_lang = to_lang
        current_text = self.input_text.toPlainText().strip()
        if current_text:
            self.translate_text(current_text)