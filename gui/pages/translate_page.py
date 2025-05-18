# gui/pages/translate_page.py
import hashlib
import json
import os
import re
import tempfile
import threading
from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout


class TranslatePage(QWidget):
    def __init__(self, main_window, translator_manager):
        super().__init__()
        self.main_window = main_window
        self.translator = translator_manager

        self.input_box = QTextEdit()
        self.output_box = QTextEdit()
        self.translate_button = QPushButton("Translate")

        layout = QVBoxLayout()
        layout.addWidget(self.input_box)
        layout.addWidget(self.translate_button)
        layout.addWidget(self.output_box)
        self.setLayout(layout)

        self.translate_button.clicked.connect(self._start_translation_thread)

        self._current_translation_id = None
        self._lock = threading.Lock()

    def _start_translation_thread(self):
        input_text = self.input_box.toPlainText().strip()
        src_lang = self.main_window.current_from_language
        dest_lang = self.main_window.current_to_language

        translation_id = hashlib.md5(input_text.encode()).hexdigest()
        self._current_translation_id = translation_id

        def update_ui(partial_result: str):
            with self._lock:
                if self._current_translation_id == translation_id:
                    self.output_box.setPlainText(partial_result)

        def run():
            self._translate_large_text(
                input_text, src_lang, dest_lang, on_chunk_done=update_ui
            )

        threading.Thread(target=run, daemon=True).start()

    def _split_by_sentences(self, text: str):
        paragraphs = text.split('\n\n')
        split_chunks = []
        for para in paragraphs:
            sentences = re.split(r'(?<=[.!?])\s+', para.strip())
            cleaned = [s.strip() for s in sentences if s.strip()]
            if cleaned:
                split_chunks.append(cleaned)
        return split_chunks

    def _translate_large_text(self, text: str, src_lang: str, dest_lang: str, on_chunk_done=None) -> str:
        split_chunks = self._split_by_sentences(text)

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tf:
            temp_path = tf.name
            json.dump(split_chunks, tf)

        with open(temp_path, 'r') as f:
            loaded_chunks = json.load(f)

        os.remove(temp_path)

        results = []
        for para_chunks in loaded_chunks:
            para_text = ' '.join(para_chunks)
            translation = self.translator.translate(para_text, src_lang, dest_lang)
            results.append(translation)

            if on_chunk_done:
                partial_result = "\n\n".join(results)
                on_chunk_done(partial_result)

        return "\n\n".join(results)
