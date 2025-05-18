from PyQt6.QtWidgets import (
    QWidget, QStackedLayout, QVBoxLayout, QPushButton, QHBoxLayout,
    QComboBox, QLabel
)
from PyQt6.QtCore import pyqtSignal
import sounddevice as sd

from services.translation_manager import TranslationManager
from gui.pages.text_to_text_page import TextToTextPage
from gui.pages.text_to_speech_page import TextToSpeechPage
from gui.pages.speech_to_text_page import SpeechToTextPage
from gui.pages.speech_to_speech_page import SpeechToSpeechPage


class MainWindow(QWidget):
    languageChanged = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

        self.languages = {
            "English": "en",
            "Arabic": "ar",
            "Urdu": "ur"
        }
        self.current_from_language = "en"
        self.current_to_language = "en"
        self.translator = TranslationManager()

        self.from_lang_combo = QComboBox()
        self.to_lang_combo = QComboBox()
        self._init_language_combos()

        main_layout = QVBoxLayout()
        main_layout.addLayout(self._create_language_layout())
        main_layout.addLayout(self._create_navigation_buttons())

        self._init_pages()
        main_layout.addLayout(self.stack)

        main_layout.addLayout(self._create_microphone_selector())
        main_layout.addLayout(self._create_speaker_selector())

        self.setLayout(main_layout)
        self.switch_page(0)
        self.languageChanged.emit(self.current_from_language, self.current_to_language)

    def _init_language_combos(self):
        for lang in self.languages:
            self.from_lang_combo.addItem(lang)
            self.to_lang_combo.addItem(lang)
        self.from_lang_combo.setCurrentText("English")
        self.to_lang_combo.setCurrentText("English")
        self.from_lang_combo.currentTextChanged.connect(self.on_language_changed)
        self.to_lang_combo.currentTextChanged.connect(self.on_language_changed)

    def _create_language_layout(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(QLabel("From:"))
        layout.addWidget(self.from_lang_combo)
        layout.addWidget(QLabel("To:"))
        layout.addWidget(self.to_lang_combo)
        return layout

    def _create_navigation_buttons(self) -> QHBoxLayout:
        self.text_to_text_btn = QPushButton("Text → Text")
        self.text_to_speech_btn = QPushButton("Text → Speech")
        self.speech_to_text_btn = QPushButton("Speech → Text")
        self.speech_to_speech_btn = QPushButton("Speech → Speech")

        self.text_to_text_btn.clicked.connect(lambda: self.switch_page(0))
        self.text_to_speech_btn.clicked.connect(lambda: self.switch_page(1))
        self.speech_to_text_btn.clicked.connect(lambda: self.switch_page(2))
        self.speech_to_speech_btn.clicked.connect(lambda: self.switch_page(3))

        layout = QHBoxLayout()
        layout.addWidget(self.text_to_text_btn)
        layout.addWidget(self.text_to_speech_btn)
        layout.addWidget(self.speech_to_text_btn)
        layout.addWidget(self.speech_to_speech_btn)
        return layout

    def _init_pages(self):
        self.text_to_text_page = TextToTextPage(self.translator, self)
        self.text_to_speech_page = TextToSpeechPage(self.translator, self)
        self.speech_to_text_page = SpeechToTextPage(self.translator, self)
        self.speech_to_speech_page = SpeechToSpeechPage(self.translator, self)

        self.pages = [
            self.text_to_text_page,
            self.text_to_speech_page,
            self.speech_to_text_page,
            self.speech_to_speech_page
        ]

        self.stack = QStackedLayout()
        for page in self.pages:
            self.stack.addWidget(page)

    def _create_microphone_selector(self) -> QHBoxLayout:
        self.mic_combo = QComboBox()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("🎤 Mic:"))
        layout.addWidget(self.mic_combo)
        self.populate_microphones()
        return layout

    def _create_speaker_selector(self) -> QHBoxLayout:
        self.speaker_combo = QComboBox()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("🔊 Speaker:"))
        layout.addWidget(self.speaker_combo)
        self.populate_speakers()
        return layout

    def populate_microphones(self):
        self.mic_combo.clear()
        try:
            for index, device in enumerate(sd.query_devices()):
                if device["max_input_channels"] > 0 and device["hostapi"] == sd.default.hostapi:
                    name = device["name"].lower()
                    if not any(v in name for v in ["virtual", "voicemeeter", "vb-audio", "cable", "obs"]):
                        label = f"{device['name']} ({device['hostapi']})"
                        self.mic_combo.addItem(label, userData=index)
        except Exception as e:
            print(f"[Mic Population Error] {e}")
            self.mic_combo.addItem("No input devices found", userData=None)

    def populate_speakers(self):
        self.speaker_combo.clear()
        try:
            for index, device in enumerate(sd.query_devices()):
                if device["max_output_channels"] > 0 and device["hostapi"] == sd.default.hostapi:
                    name = device["name"].lower()
                    if not any(v in name for v in ["virtual", "voicemeeter", "vb-audio", "cable", "obs"]):
                        label = f"{device['name']} ({device['hostapi']})"
                        self.speaker_combo.addItem(label, userData=index)
        except Exception as e:
            print(f"[Speaker Population Error] {e}")
            self.speaker_combo.addItem("No output devices found", userData=None)

    def on_language_changed(self):
        from_lang = self.languages.get(self.from_lang_combo.currentText(), "en")
        to_lang = self.languages.get(self.to_lang_combo.currentText(), "en")
        self.current_from_language = from_lang
        self.current_to_language = to_lang
        self.languageChanged.emit(from_lang, to_lang)

    def set_languages(self, from_lang: str, to_lang: str):
        from_label = next((k for k, v in self.languages.items() if v == from_lang), None)
        to_label = next((k for k, v in self.languages.items() if v == to_lang), None)
        if from_label:
            self.from_lang_combo.setCurrentText(from_label)
        if to_label:
            self.to_lang_combo.setCurrentText(to_label)
        self.languageChanged.emit(from_lang, to_lang)

    def switch_page(self, index: int):
        current_index = self.stack.currentIndex()
        if 0 <= current_index < len(self.pages):
            current_page = self.pages[current_index]
            if hasattr(current_page, "reset"):
                current_page.reset()  # Ensure clean cancellation/reset

        self.stack.setCurrentIndex(index)

    def get_selected_input_device_index(self):
        return self.mic_combo.currentData()

    def get_selected_output_device_index(self):
        return self.speaker_combo.currentData() 