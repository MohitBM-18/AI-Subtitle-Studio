"""
Translation service – translates subtitle text via OpenAI GPT.
Architecture note: swap this module's implementation to switch to DeepL, Google
Translate, or any other provider without touching the rest of the application.
"""
from openai import OpenAI
from backend.config import settings


def translate_text(text: str, target_language: str) -> str:
    """
    Translate *text* into *target_language* (e.g. "English", "Hindi", "Spanish").
    Preserves names, punctuation and conversational tone.
    Returns the translated string.
    """
    if not text.strip():
        return text

    client = OpenAI(api_key=settings.openai_api_key)

    system_prompt = (
        f"You are a professional subtitle translator. "
        f"Translate the following subtitle text into {target_language}. "
        f"Rules:\n"
        f"- Preserve proper nouns and names exactly.\n"
        f"- Keep punctuation consistent with the original.\n"
        f"- Match the conversational register (formal/informal).\n"
        f"- Output ONLY the translated text, nothing else."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": text},
        ],
        temperature=0.1,
        max_tokens=2000,
    )

    return response.choices[0].message.content.strip()
