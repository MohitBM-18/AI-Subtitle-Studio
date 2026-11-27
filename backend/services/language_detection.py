"""
Language detection service.
Uses OpenAI Whisper (verbose_json) to detect the spoken language automatically.
"""
from pathlib import Path
from openai import OpenAI
from backend.config import settings


def detect_language(audio_path: Path) -> tuple[str, float]:
    """
    Returns (language_code, confidence).
    language_code is an ISO-639-1 code, e.g. 'en', 'hi', 'kn'.
    Confidence is 0.0–1.0 (Whisper does not expose raw confidence; we return 1.0 as a placeholder).
    """
    client = OpenAI(api_key=settings.openai_api_key)

    with open(audio_path, "rb") as audio_file:
        # verbose_json gives us the detected language field
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
        )

    language = getattr(response, "language", "unknown") or "unknown"
    return language, 1.0
