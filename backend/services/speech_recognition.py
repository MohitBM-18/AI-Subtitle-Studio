"""
Speech recognition service – full transcription with word-level timestamps.
Uses OpenAI Whisper (verbose_json) for maximum accuracy.
"""
from pathlib import Path
from typing import List
from openai import OpenAI
from backend.config import settings
from backend.models.schemas import WordTimestamp, SubtitleSegment


def transcribe(audio_path: Path) -> dict:
    """
    Returns a dict with:
        language   : detected ISO-639-1 code
        full_text  : complete transcript
        segments   : list of SubtitleSegment (sentence-level, with word timestamps)
    """
    client = OpenAI(api_key=settings.openai_api_key)

    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
            temperature=0.0,   # deterministic – prioritise accuracy
        )

    language  = getattr(response, "language", "en") or "en"
    full_text = getattr(response, "text", "")

    # Build structured segments
    raw_segments = getattr(response, "segments", []) or []
    raw_words    = getattr(response, "words",    []) or []

    # Map words to segments
    word_map: dict[int, List[WordTimestamp]] = {}
    for seg in raw_segments:
        word_map[seg.id] = []

    for w in raw_words:
        # Whisper word objects have .word, .start, .end
        wt = WordTimestamp(
            word=w.word,
            start=w.start,
            end=w.end,
        )
        # Assign word to its segment (match by time overlap)
        for seg in raw_segments:
            if seg.start <= w.start < seg.end:
                word_map.setdefault(seg.id, []).append(wt)
                break

    segments: List[SubtitleSegment] = []
    for seg in raw_segments:
        segments.append(SubtitleSegment(
            text=seg.text.strip(),
            start=seg.start,
            end=seg.end,
            words=word_map.get(seg.id, []),
        ))

    return {
        "language": language,
        "full_text": full_text,
        "segments": segments,
    }
