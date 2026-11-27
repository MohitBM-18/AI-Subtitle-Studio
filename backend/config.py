"""
AI Subtitle Studio – Centralised configuration loaded from .env
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator


BASE_DIR = Path(__file__).resolve().parent.parent  # project root


class Settings(BaseSettings):
    # ── Server ────────────────────────────────────────────────
    host: str = "127.0.0.1"
    port: int = 8000

    # ── OpenAI ────────────────────────────────────────────────
    openai_api_key: str = ""

    # ── Upload limits ─────────────────────────────────────────
    max_video_size_mb: int = 500
    max_video_duration_seconds: int = 3600
    allowed_extensions: str = ".mp4,.mov,.mkv,.avi,.webm"

    # ── Storage ───────────────────────────────────────────────
    upload_dir: str = "storage/uploads"
    temp_dir:   str = "storage/temporary"
    output_dir: str = "storage/outputs"

    # ── CORS ──────────────────────────────────────────────────
    cors_origins: list[str] = ["*"]

    # ── Cleanup ───────────────────────────────────────────────
    cleanup_after_hours: int = 24

    model_config = {"env_file": str(BASE_DIR / ".env"), "extra": "ignore"}

    # ── Computed paths ────────────────────────────────────────
    @property
    def upload_path(self) -> Path:
        p = BASE_DIR / self.upload_dir
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def temp_path(self) -> Path:
        p = BASE_DIR / self.temp_dir
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def output_path(self) -> Path:
        p = BASE_DIR / self.output_dir
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def allowed_ext_set(self) -> set:
        return {e.strip().lower() for e in self.allowed_extensions.split(",")}


settings = Settings()
