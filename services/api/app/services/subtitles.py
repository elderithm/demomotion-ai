from pathlib import Path


def create_vtt(script: str, output_path: Path) -> str:
    lines = [line.strip() for line in script.splitlines() if line.strip()]
    if not lines:
        lines = [script.strip()]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunks = ["WEBVTT", ""]
    start = 0
    for idx, line in enumerate(lines, start=1):
        end = start + 4
        chunks.append(str(idx))
        chunks.append(f"00:00:{start:02d}.000 --> 00:00:{end:02d}.000")
        chunks.append(line)
        chunks.append("")
        start = end
    text = "\n".join(chunks)
    output_path.write_text(text, encoding="utf-8")
    return text
