# services/translation_manager.py

import threading
import re
from typing import Optional, Callable, List, Dict
from services.translators import Translator, MarianTranslator, GoogleTranslator, LlamaTranslator


class TranslationManager:
    def __init__(self):
        self.google: Optional[GoogleTranslator] = None
        self.marian: Optional[MarianTranslator] = None
        self.llama: Optional[LlamaTranslator] = None

    def _load_translators(self):
        if not self.google:
            self.google = GoogleTranslator()
        if not self.marian:
            self.marian = MarianTranslator()
        if not self.llama:
            self.llama = LlamaTranslator()

    def _split_into_chunks(self, text: str, max_sentences_per_chunk: int = 3) -> List[str]:
        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        chunks = []
        for i in range(0, len(sentences), max_sentences_per_chunk):
            chunk = ' '.join(sentences[i:i + max_sentences_per_chunk])
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    def translate(self, text: str, src_lang: str, dest_lang: str, on_chunk_done: Optional[Callable[[str], None]] = None) -> str:
        self._load_translators()

        if src_lang == dest_lang:
            return text

        chunks = self._split_into_chunks(text)
        final_output: List[str] = []

        for i in range(0, len(chunks), 2):
            group_chunks = chunks[i:i + 2]
            group_text = '\n'.join(group_chunks)

            results: Dict[str, Optional[str]] = {
                "google": None,
                "marian": None,
                "llama": None
            }

            def run_translator(name: str, translator: Translator):
                try:
                    if name == "llama":
                        # Wait for others to complete first
                        while results["google"] is None and results["marian"] is None:
                            pass  # Busy wait (can be improved using Condition)
                        candidates = [r for r in [results["google"], results["marian"]] if r and r.strip().lower() != group_text.strip().lower()]
                        if not candidates:
                            results["llama"] = "\u274c No valid candidates for LLaMA."
                            return
                        results["llama"] = self.llama.translate(group_text, src_lang, dest_lang, candidates)
                    else:
                        results[name] = translator.translate(group_text, src_lang, dest_lang)
                except Exception as e:
                    print(f"[{name}] failed: {e}")
                    results[name] = None

            threads = [
                threading.Thread(target=run_translator, args=("google", self.google)),
                threading.Thread(target=run_translator, args=("marian", self.marian)),
                threading.Thread(target=run_translator, args=("llama", self.llama))
            ]

            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=30)

            # Choose best translation
            if results["llama"] and not results["llama"].startswith("\u274c"):
                final_output.append(results["llama"])
            else:
                candidates = [r for r in [results["google"], results["marian"]] if r and r.strip().lower() != group_text.strip().lower()]
                if not candidates:
                    final_output.append("\u274c Translation failed for chunk.")
                else:
                    final_output.append(candidates[0])

            # Emit partial output for UI update (threaded call to avoid blocking)
            if on_chunk_done:
                partial_result = "\n\n".join(final_output)
                threading.Thread(target=on_chunk_done, args=(partial_result,), daemon=True).start()

        return "\n\n".join(final_output)