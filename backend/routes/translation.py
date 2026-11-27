"""
Translation route – translates an existing SRT subtitle file line-by-line.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.config import settings
from backend.models.schemas import TranslationRequest, TranslationResponse
from backend.services.translation import translate_text

router = APIRouter()


@router.post(
    "/translate",
    response_model=TranslationResponse,
    summary="Translate subtitle file into another language",
)
async def translate_subtitles(req: TranslationRequest):
    """
    Reads a source SRT file, translates every text line (preserving timestamps),
    and writes a new translated SRT.
    """
    sub_dir  = settings.temp_path / f"sub_{req.video_id}"
    src_path = sub_dir / req.source_srt
    if not src_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Source subtitle '{req.source_srt}' not found. Run /transcribe first."
        )

    # Parse SRT: collect (index, timestamp_line, text_lines) blocks
    raw = src_path.read_text(encoding="utf-8")
    blocks = _parse_srt(raw)

    # Translate text lines
    translated_blocks = []
    for idx, timestamp, text_lines in blocks:
        combined = " ".join(text_lines)
        try:
            translated = translate_text(combined, req.target_language)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Translation failed: {exc}")
        translated_blocks.append((idx, timestamp, translated))

    # Write translated SRT
    out_name = f"translated_{req.target_language.replace(' ', '_')}_{req.source_srt}"
    out_path = sub_dir / out_name
    out_path.write_text(_build_srt(translated_blocks), encoding="utf-8")

    return TranslationResponse(
        video_id=req.video_id,
        target_language=req.target_language,
        translated_srt=out_name,
    )


# ── SRT parse / build helpers ─────────────────────────────────────────────────
def _parse_srt(raw: str):
    """Return list of (index_str, timestamp_line, [text_lines])."""
    blocks = []
    for block in raw.strip().split("\n\n"):
        lines = [l for l in block.splitlines() if l.strip()]
        if len(lines) < 3:
            continue
        idx       = lines[0]
        timestamp = lines[1]
        text      = lines[2:]
        blocks.append((idx, timestamp, text))
    return blocks


def _build_srt(blocks) -> str:
    parts = []
    for idx, timestamp, translated in blocks:
        parts.append(f"{idx}\n{timestamp}\n{translated}")
    return "\n\n".join(parts) + "\n"
