import re
from pathlib import Path


def _sentences(text: str) -> list[str]:
    """Split narration into sentences for both Japanese (。！？) and Latin (.!?)."""
    text = text.replace("\n", " ").strip()
    parts = re.split(r"(?<=[。！？!?\.])\s*", text)
    return [p.strip() for p in parts if p.strip()]


def _fmt(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def create_vtt(script: str, output_path: Path, total_duration: float | None = None) -> str:
    """Build a WebVTT track. Cues are one sentence each, spread across the
    narration length (proportional to sentence length) so the subtitles track
    the voice-over instead of all showing up in the first few seconds."""
    sentences = _sentences(script) or [script.strip()]
    total_chars = sum(len(s) for s in sentences) or 1
    if not total_duration or total_duration <= 0:
        total_duration = 4.0 * len(sentences)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunks = ["WEBVTT", ""]
    t = 0.0
    for idx, sentence in enumerate(sentences, start=1):
        dur = total_duration * (len(sentence) / total_chars)
        start, end = t, t + dur
        chunks.append(str(idx))
        chunks.append(f"{_fmt(start)} --> {_fmt(end)}")
        chunks.append(sentence)
        chunks.append("")
        t = end

    text = "\n".join(chunks)
    output_path.write_text(text, encoding="utf-8")
    return text
