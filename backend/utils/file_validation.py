"""
File validation utilities
"""
from pathlib import Path
from backend.config import settings


def validate_upload(file_path: Path) -> tuple[bool, str]:
    """Return (ok, error_message). Call after the file is saved to disk."""
    suffix = file_path.suffix.lower()
    if suffix not in settings.allowed_ext_set:
        return False, (
            f"Unsupported file type '{suffix}'. "
            f"Allowed: {', '.join(sorted(settings.allowed_ext_set))}"
        )
    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > settings.max_video_size_mb:
        return False, (
            f"File size {size_mb:.1f} MB exceeds the {settings.max_video_size_mb} MB limit."
        )
    return True, ""
