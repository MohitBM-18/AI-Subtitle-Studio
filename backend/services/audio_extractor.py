"""
Audio extraction service – pulls the audio track from a video using FFmpeg.
Outputs a 16 kHz mono WAV which is optimal for Whisper transcription.
"""
import subprocess
from pathlib import Path


def extract_audio(video_path: Path, out_wav: Path) -> None:
    """
    Extract audio from *video_path* and write a 16 kHz mono WAV to *out_wav*.
    Raises subprocess.CalledProcessError on FFmpeg failure.
    """
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",           # drop video stream
        "-ac", "1",      # mono
        "-ar", "16000",  # 16 kHz – ideal for Whisper
        "-sample_fmt", "s16",
        str(out_wav),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed:\n{result.stderr}")
