"""
Upload route – streaming multipart file upload with validation.
"""
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config import settings
from backend.models.schemas import UploadResponse
from backend.utils.file_validation import validate_upload

router = APIRouter()

CHUNK_SIZE = 1024 * 1024  # 1 MB chunks – never loads entire file into memory


@router.post("/upload", response_model=UploadResponse, summary="Upload a video file")
async def upload_video(file: UploadFile = File(...)):
    """
    Accept a video upload, stream it to disk, then validate it.
    Returns a *video_id* used by all subsequent API calls.
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in settings.allowed_ext_set:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{suffix}' is not supported. Allowed: {', '.join(sorted(settings.allowed_ext_set))}",
        )

    video_id  = str(uuid.uuid4())
    dest_name = f"{video_id}{suffix}"
    dest_path = settings.upload_path / dest_name

    # Stream to disk
    try:
        with dest_path.open("wb") as out:
            while chunk := await file.read(CHUNK_SIZE):
                out.write(chunk)
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")

    # Size validation after save
    ok, err = validate_upload(dest_path)
    if not ok:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=err)

    size_mb = dest_path.stat().st_size / (1024 * 1024)
    return UploadResponse(
        video_id=dest_name,
        original_filename=file.filename,
        size_mb=round(size_mb, 2),
    )
