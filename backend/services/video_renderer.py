"""
Video renderer – burns subtitles permanently into the video using FFmpeg.
The output is a standard H.264 MP4 that plays on any device or platform.
"""
import subprocess
from pathlib import Path


# Resolution presets
RESOLUTION_MAP = {
    "same":      None,
    "1080p":     "1920x1080",
    "720p":      "1280x720",
    "480p":      "854x480",
    "portrait":  "1080x1920",
    "square":    "1080x1080",
}


def burn_subtitles(
    video_path: Path,
    subtitle_path: Path,
    output_path: Path,
    resolution: str = "same",
    crf: int = 18,              # quality: 18 = nearly lossless, 28 = smaller file
) -> None:
    """
    Burn *subtitle_path* (SRT) permanently into *video_path* and write to *output_path*.

    Args:
        video_path    – source video file
        subtitle_path – UTF-8 SRT subtitle file
        output_path   – destination MP4
        resolution    – "same" | "1080p" | "720p" | "480p" | "portrait" | "square"
        crf           – constant rate factor (lower = better quality, larger file)
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # FFmpeg subtitles filter needs forward slashes + escaped colons on Windows
    srt_escaped = str(subtitle_path).replace("\\", "/").replace(":", "\\:")

    # Build scale + subtitle filter chain
    target_res = RESOLUTION_MAP.get(resolution)
    if target_res:
        vf = f"scale={target_res}:force_original_aspect_ratio=decrease,subtitles='{srt_escaped}'"
    else:
        vf = f"subtitles='{srt_escaped}'"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", str(crf),
        "-c:a", "copy",          # keep original audio untouched
        "-movflags", "+faststart",  # enables streaming / quick web playback
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg render failed:\n{result.stderr}")
