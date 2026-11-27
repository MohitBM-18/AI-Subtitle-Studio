"""
Automatic cleanup of expired temporary and output files.
Called from background tasks or on a schedule.
"""
import time
from pathlib import Path
from backend.config import settings


def purge_expired_files() -> int:
    """Delete files older than CLEANUP_AFTER_HOURS. Returns count of deleted files."""
    cutoff = time.time() - settings.cleanup_after_hours * 3600
    deleted = 0
    for folder in [settings.upload_path, settings.temp_path, settings.output_path]:
        for item in folder.rglob("*"):
            if item.is_file() and item.stat().st_mtime < cutoff:
                item.unlink(missing_ok=True)
                deleted += 1
    return deleted
