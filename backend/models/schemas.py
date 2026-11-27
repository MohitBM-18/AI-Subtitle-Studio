"""
Pydantic schemas shared across the application
"""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel


# ── Upload ────────────────────────────────────────────────────────────────────
class UploadResponse(BaseModel):
    video_id: str
    original_filename: str
    size_mb: float
    message: str = "Upload successful"


# ── Word / segment timestamps ─────────────────────────────────────────────────
class WordTimestamp(BaseModel):
    word: str
    start: float
    end: float
    confidence: Optional[float] = None


class SubtitleSegment(BaseModel):
    text: str
    start: float
    end: float
    words: Optional[List[WordTimestamp]] = None


# ── Transcription ─────────────────────────────────────────────────────────────
class TranscriptionResponse(BaseModel):
    video_id: str
    language: str
    language_confidence: Optional[float] = None
    segments: List[SubtitleSegment]
    full_text: str
    subtitle_srt: str          # name of .srt file in temp folder


# ── Translation ───────────────────────────────────────────────────────────────
class TranslationRequest(BaseModel):
    video_id: str
    target_language: str       # e.g. "English", "Hindi", "Spanish"
    source_srt: str            # name of source .srt file


class TranslationResponse(BaseModel):
    video_id: str
    target_language: str
    translated_srt: str        # name of translated .srt file


# ── Render ────────────────────────────────────────────────────────────────────
class RenderRequest(BaseModel):
    video_id: str
    subtitle_file: str
    resolution: str = "same"   # "same" | "1920x1080" | "1280x720" | "854x480"
    subtitle_style: dict = {}


class RenderResponse(BaseModel):
    output_video: str
    download_url: str


# ── Job status ────────────────────────────────────────────────────────────────
class JobStatus(BaseModel):
    job_id: str
    status: str                # "queued" | "processing" | "done" | "failed"
    stage: Optional[str] = None
    progress: int = 0          # 0-100
    result: Optional[dict] = None
    error: Optional[str] = None
