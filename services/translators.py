import requests
import subprocess
from abc import ABC, abstractmethod
from typing import Optional
from transformers.models.marian import MarianMTModel, MarianTokenizer
import torch


class Translator(ABC):
    @abstractmethod
    def translate(self, text: str, src_lang: str, dest_lang: str) -> Optional[str]:
        pass

    @property
    def name(self):
        return self.__class__.__name__


class GoogleTranslator(Translator):
    def translate(self, text: str, src_lang: str, dest_lang: str) -> Optional[str]:
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {"client": "gtx", "sl": src_lang, "tl": dest_lang, "dt": "t", "q": text}
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return "".join([t[0] for t in data[0]])
        except Exception as e:
            print(f"[GoogleTranslator] failed: {e}")
        return None


class LlamaTranslator(Translator):
    """
    LlamaTranslator: A language translation class leveraging the Llama model via the Ollama CLI.
    This class provides an interface to translate text between languages using the Llama language model.
    It supports both direct translation and selection of the best translation from a list of candidates.
    The translation is performed by constructing a prompt and invoking the Llama model through a subprocess call.
    Usage:
        translator = LlamaTranslator()
        result = translator.translate("Hello", "English", "Spanish")
    """
    def translate(self, text: str, src_lang: str, dest_lang: str, candidates: Optional[list[str]] = None) -> Optional[str]:
        if candidates:
            prompt = (
                f"You are an expert in language translation. You are given a phrase in {src_lang}, "
                f"and multiple translations to {dest_lang}. Choose the most accurate and natural translation.\n\n"
                f"Original: {text}\n\n"
                "Candidates:\n"
            )
            for i, c in enumerate(candidates):
                prompt += f"{i+1}. {c}\n"
            prompt += "\nOnly output the best translation without any explanation."
        else:
            prompt = (
                f"Translate from {src_lang} to {dest_lang}.\n"
                f"ONLY output the translated text.\n"
                f"Here is the text:\n\"{text}\"\n"
                f"Translation:"
            )

        try:
            result = subprocess.run(
                ["ollama", "run", "llama3"],
                input=prompt.encode("utf-8"),
                capture_output=True,
                timeout=60
            )
            response = result.stdout.decode("utf-8").strip().splitlines()[0]
            if candidates:
                for c in candidates:
                    if c.strip() in response:
                        return c.strip()
            return response
        except Exception as e:
            print(f"[LlamaTranslator] failed: {e}")
        return None


class MarianTranslator(Translator):
    def __init__(self):
        self.models = {}
        preload_pairs = [('en', 'ur'), ('ur', 'en')]
        for src, tgt in preload_pairs:
            self.load_model(src, tgt)

    def load_model(self, src_lang: str, tgt_lang: str):
        if src_lang == tgt_lang:
            return None, None

        model_name = f'Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}'
        if (src_lang, tgt_lang) not in self.models:
            print(f"[MarianTranslator] Loading model: {model_name}")
            try:
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)
                self.models[(src_lang, tgt_lang)] = (tokenizer, model)
            except Exception as e:
                print(f"[MarianTranslator] Failed to load {model_name}: {e}")
                return None, None
        return self.models[(src_lang, tgt_lang)]

    def translate(self, text: str, src_lang: str, dest_lang: str) -> Optional[str]:
        if src_lang == dest_lang:
            return text

        tokenizer, model = self.load_model(src_lang, dest_lang)
        if tokenizer is None or model is None:
            return None

        batch = tokenizer([text], return_tensors="pt", padding=True)
        gen = model.generate(**batch)
        translation = tokenizer.batch_decode(gen, skip_special_tokens=True)[0]
        return translation