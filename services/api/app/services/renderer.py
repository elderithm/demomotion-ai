from pathlib import Path
import subprocess


def _duration(path: Path) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nokey=1:noprint_wrappers=1", str(path)],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        return float(out.stdout.strip() or 0)
    except Exception:
        return 0.0


_SUBTITLE_STYLE = (
    "FontSize=22,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,"
    "BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=40"
)


class VideoRenderer:
    def render(
        self, raw_video: Path, audio: Path, subtitle_vtt: Path, output_path: Path,
        trim_start: float = 0.0,
    ) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        video_dur = _duration(raw_video)
        audio_dur = _duration(audio)

        # Drop the blank load/hydration lead-in at the start of the recording (plus
        # a small buffer for paint lag after the DOM fills), but never trim so much
        # that little content is left. Narration and subtitles are both 0-based, so
        # dropping the video's blank head lines the content up with the voice-over.
        trim = max(0.0, min(trim_start + 0.4, video_dur - 3.0))
        content_dur = max(0.0, video_dur - trim)

        # Make the output run for the longer of content vs narration so the
        # narration is never cut off: hold (freeze) the last video frame while the
        # voice-over finishes.
        target = max(content_dur, audio_dur) + 0.3
        video_pad = max(0.0, target - content_dur)

        # Frame-accurate trim (unlike -ss keyframe seeking, this leaves no sliver of
        # the blank intro), then hold the last frame to reach the target length.
        head = f"trim=start={trim:.2f},setpts=PTS-STARTPTS," if trim > 0 else ""
        pad = f"[0:v]{head}tpad=stop_mode=clone:stop_duration={video_pad:.2f}"

        def command(burn_subtitles: bool) -> list[str]:
            vfilter = pad
            if burn_subtitles:
                # Burn the WebVTT captions into the frames. force_style is quoted so
                # its commas are not read as filter separators.
                vfilter += f",subtitles={subtitle_vtt}:force_style='{_SUBTITLE_STYLE}'"
            vfilter += "[v]"
            return [
                "ffmpeg", "-y",
                "-i", str(raw_video),
                "-i", str(audio),
                "-filter_complex", vfilter,
                "-map", "[v]",
                "-map", "1:a:0",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-t", f"{target:.2f}",
                str(output_path),
            ]

        # Prefer burned-in subtitles; if that fails (e.g. missing fonts), retry
        # without them so the video + narration still render.
        want_subs = bool(subtitle_vtt and Path(subtitle_vtt).exists())
        for burn in ([True, False] if want_subs else [False]):
            try:
                subprocess.run(command(burn), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return output_path
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        # ffmpeg unavailable: return the raw recording so the pipeline still yields
        # an artifact.
        output_path.write_bytes(raw_video.read_bytes())
        return output_path
