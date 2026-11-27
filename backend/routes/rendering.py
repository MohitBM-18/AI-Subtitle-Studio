"""
Rendering route – burn subtitles permanently into the video with FFmpeg.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.config import settings
from backend.models.schemas import RenderRequest, RenderResponse
from backend.services.video_renderer import burn_subtitles
import uuid

router = APIRouter()


@router.post(
    "/render",
    response_model=RenderResponse,
    summary="Burn subtitles into the video and produce a downloadable MP4",
)
async def render_video(req: RenderRequest):
    """
    Takes a video_id and a subtitle SRT filename, runs FFmpeg to permanently
    embed the subtitles, and returns a download URL.
    """
    video_path = settings.upload_path / req.video_id
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"Video '{req.video_id}' not found.")

    sub_path = settings.temp_path / f"sub_{req.video_id}" / req.subtitle_file
    if not sub_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Subtitle file '{req.subtitle_file}' not found. Run transcribe/translate first."
        )

    out_name = f"final_{uuid.uuid4()}.mp4"
    out_path = settings.output_path / out_name

    try:
        burn_subtitles(
            video_path=video_path,
            subtitle_path=sub_path,
            output_path=out_path,
            resolution=req.resolution,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=f"Rendering failed: {exc}")

    return RenderResponse(
        output_video=out_name,
        download_url=f"/api/videos/{out_name}",
    )


@router.get("/videos/{video_name}", summary="Stream / download a rendered video")
async def download_video(video_name: str):
    # Security: strip path traversal attempts
    safe_name = Path(video_name).name
    video_path = settings.output_path / safe_name
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail="Video not found or has expired.")

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=safe_name,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )
