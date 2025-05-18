# Multilingual AI-Based Translation Application

## Introduction

This project is a powerful AI-driven multilingual translation application built to support real-time communication across language boundaries using both voice and text. It is designed for use in educational, professional, and casual environments, helping users translate speech and text quickly and efficiently.

###  Supported Translation Modes:
- **Speech-to-Speech (S2S)** – Speak and hear your translated voice output.
- **Speech-to-Text (S2T)** – Speak and get instant translated text.
- **Text-to-Speech (T2S)** – Type and listen to the translated speech.
- **Text-to-Text (T2T)** – Translate written content across supported languages.

### Supported Languages:
- **English**
- **Urdu**
- **Arabic**

>  Only these three languages are currently supported across all modes.

### System Recommendations:
- **Python Version**: Recommended to use **Python 3.11.9**
- **Minimum RAM**: At least **4 GB** RAM is recommended for smooth performance.
- **Note**: The application may **freeze temporarily during translation**, especially when using LLaMA in the background. Please **be patient and wait** while it completes the task.

###  LLaMA Model Requirement:
Make sure that the **LLaMA 3 model is properly installed and running locally** (e.g., via **Ollama** or another compatible CLI interface). This is essential for deep translation validation.

###  First Run Notice:
On the **first launch**, the application may take a few **minutes to download required translation models** (e.g., MarianMT via Hugging Face). This happens in the background, so please **wait patiently**.

### Before Running:
Install all required dependencies using:

```bash
pip install -r requirements.txt
