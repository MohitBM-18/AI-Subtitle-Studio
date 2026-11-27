"""
Transcription route – audio extraction → language detection → Whisper transcription.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from backend.config import settings
from backend.models.schemas import TranscriptionResponse
from backend.services.audio_extractor import extract_audio
from backend.services.language_detection import detect_language
from backend.services.speech_recognition import transcribe
from backend.services.subtitle_generator import write_karaoke_srt, write_sentence_srt

router = APIRouter()


@router.post(
    "/transcribe/{video_id}",
    response_model=TranscriptionResponse,
    summary="Transcribe a video and generate subtitles",
)
async def transcribe_video(
    video_id: str,
    style: str = Query("sentence", enum=["karaoke", "sentence"]),
):
    """
    1. Extract audio from the uploaded video.
    2. Auto-detect spoken language.
    3. Transcribe with word-level timestamps.
    4. Write an SRT subtitle file (karaoke or sentence style).
    """
    video_path = settings.upload_path / video_id
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found.")

    # ── 1. Extract audio ──────────────────────────────────────────────────────
    audio_path = settings.temp_path / f"{video_id}.wav"
    try:
        extract_audio(video_path, audio_path)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=f"Audio extraction failed: {exc}")

    # ── 2 & 3. Transcribe (also gives us language) ───────────────────────────
    try:
        result = transcribe(audio_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}")

    segments   = result["segments"]
    language   = result["language"]
    full_text  = result["full_text"]

    if not segments:
        raise HTTPException(status_code=422, detail="No speech detected in the video.")

    # ── 4. Write SRT ─────────────────────────────────────────────────────────
    sub_dir  = settings.temp_path / f"sub_{video_id}"
    srt_name = f"{style}_{video_id}.srt"
    srt_path = sub_dir / srt_name

    if style == "karaoke":
        write_karaoke_srt(segments, srt_path)
    else:
        write_sentence_srt(segments, srt_path)

    return TranscriptionResponse(
        video_id=video_id,
        language=language,
        segments=segments,
        full_text=full_text,
        subtitle_srt=srt_name,
    )
