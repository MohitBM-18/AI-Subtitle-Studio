"""
Subtitle generator – produces SRT files for both karaoke and sentence styles.
"""
from pathlib import Path
from typing import List
from backend.models.schemas import SubtitleSegment


# ── Helpers ───────────────────────────────────────────────────────────────────
def _fmt(seconds: float) -> str:
    """Convert seconds to SRT timestamp: HH:MM:SS,mmm"""
    h  = int(seconds // 3600)
    m  = int((seconds % 3600) // 60)
    s  = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# ── Karaoke style (one subtitle entry per WORD) ───────────────────────────────
def write_karaoke_srt(segments: List[SubtitleSegment], out_path: Path) -> None:
    """
    Each SRT cue contains a single word.  The player shows only the active word,
    creating a word-by-word highlight effect.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    counter = 1
    lines = []
    for seg in segments:
        words = seg.words or []
        if not words:
            # Fallback: treat the whole segment as one cue
            lines.append(f"{counter}\n{_fmt(seg.start)} --> {_fmt(seg.end)}\n{seg.text}\n")
            counter += 1
            continue
        for w in words:
            lines.append(f"{counter}\n{_fmt(w.start)} --> {_fmt(w.end)}\n{w.word.strip()}\n")
            counter += 1

    out_path.write_text("\n".join(lines), encoding="utf-8")


# ── Sentence style (one subtitle entry per SEGMENT) ───────────────────────────
def write_sentence_srt(segments: List[SubtitleSegment], out_path: Path,
                       max_chars: int = 80) -> None:
    """
    Each SRT cue is one sentence / segment.
    Long segments are wrapped at *max_chars* per line.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, seg in enumerate(segments, start=1):
        text = _wrap(seg.text, max_chars)
        lines.append(f"{i}\n{_fmt(seg.start)} --> {_fmt(seg.end)}\n{text}\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def _wrap(text: str, max_chars: int) -> str:
    """Wrap text so no line exceeds max_chars."""
    words = text.split()
    out_lines, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 <= max_chars:
            current = (current + " " + w).lstrip()
        else:
            if current:
                out_lines.append(current)
            current = w
    if current:
        out_lines.append(current)
    return "\n".join(out_lines)


# ── Both styles side-by-side (original + translated) ─────────────────────────
def write_bilingual_srt(
    segments: List[SubtitleSegment],
    translated_texts: List[str],
    out_path: Path,
) -> None:
    """
    Each cue shows the original text on line 1 and the translation on line 2.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, (seg, trans) in enumerate(zip(segments, translated_texts), start=1):
        lines.append(
            f"{i}\n{_fmt(seg.start)} --> {_fmt(seg.end)}\n{seg.text}\n{trans}\n"
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")
