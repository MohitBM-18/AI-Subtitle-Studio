"""
Jobs route – in-memory job tracking for async processing status.
In production, replace the in-memory store with Redis / Celery.
"""
import uuid
from typing import Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.models.schemas import JobStatus
from backend.config import settings
from backend.services.audio_extractor import extract_audio
from backend.services.speech_recognition import transcribe
from backend.services.translation import translate_text
from backend.services.subtitle_generator import write_karaoke_srt, write_sentence_srt
from backend.services.video_renderer import burn_subtitles
from pathlib import Path

router = APIRouter()

# ── In-memory job store ───────────────────────────────────────────────────────
_jobs: Dict[str, JobStatus] = {}


def _update(job: JobStatus, stage: str, progress: int):
    job.stage    = stage
    job.progress = progress
    job.status   = "processing"


# ── Full pipeline background task ─────────────────────────────────────────────
def _run_pipeline(
    job_id: str,
    video_id: str,
    style: str,
    target_lang: str | None,
    resolution: str,
):
    job = _jobs[job_id]
    try:
        video_path = settings.upload_path / video_id

        # 1. Extract audio
        _update(job, "Extracting audio", 10)
        audio_path = settings.temp_path / f"{video_id}.wav"
        extract_audio(video_path, audio_path)

        # 2 & 3. Transcribe
        _update(job, "Transcribing speech", 30)
        result   = transcribe(audio_path)
        segments = result["segments"]
        language = result["language"]

        # 4. Write original SRT
        _update(job, "Generating subtitles", 55)
        sub_dir  = settings.temp_path / f"sub_{video_id}"
        srt_name = f"{style}_{video_id}.srt"
        srt_path = sub_dir / srt_name
        if style == "karaoke":
            write_karaoke_srt(segments, srt_path)
        else:
            write_sentence_srt(segments, srt_path)

        active_srt = srt_path

        # 5. Optional translation
        if target_lang:
            _update(job, f"Translating to {target_lang}", 70)
            raw     = srt_path.read_text(encoding="utf-8")
            blocks  = []
            for block in raw.strip().split("\n\n"):
                lines = [l for l in block.splitlines() if l.strip()]
                if len(lines) >= 3:
                    blocks.append((lines[0], lines[1], " ".join(lines[2:])))
            translated_parts = []
            for idx, ts, text in blocks:
                translated_parts.append(f"{idx}\n{ts}\n{translate_text(text, target_lang)}")
            t_srt_name = f"translated_{srt_name}"
            t_srt_path = sub_dir / t_srt_name
            t_srt_path.write_text("\n\n".join(translated_parts) + "\n", encoding="utf-8")
            active_srt = t_srt_path

        # 6. Render
        _update(job, "Rendering video", 85)
        out_name = f"final_{job_id}.mp4"
        out_path = settings.output_path / out_name
        burn_subtitles(video_path, active_srt, out_path, resolution=resolution)

        job.status   = "done"
        job.progress = 100
        job.stage    = "Complete"
        job.result   = {
            "output_video": out_name,
            "download_url": f"/api/videos/{out_name}",
            "language": language,
        }

    except Exception as exc:
        job.status = "failed"
        job.error  = str(exc)


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/jobs/process", response_model=JobStatus, summary="Start full processing pipeline")
async def start_job(
    background: BackgroundTasks,
    video_id: str,
    style: str = "sentence",
    target_lang: str | None = None,
    resolution: str = "same",
):
    job_id = str(uuid.uuid4())
    job = JobStatus(job_id=job_id, status="queued", stage="Queued", progress=0)
    _jobs[job_id] = job

    background.add_task(_run_pipeline, job_id, video_id, style, target_lang, resolution)
    return job


@router.get("/jobs/{job_id}", response_model=JobStatus, summary="Poll job status")
async def get_job(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    return _jobs[job_id]


@router.delete("/jobs/{job_id}", summary="Cancel / delete a job")
async def delete_job(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    _jobs.pop(job_id)
    return {"message": f"Job {job_id} deleted."}
