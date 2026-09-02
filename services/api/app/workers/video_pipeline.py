from pathlib import Path
import traceback

from app.core.config import get_settings
from app.models.video_job import VideoJob, VideoJobStatus
from app.services.planner import NarrationWriter, ScenarioPlanner
from app.services.recorder import BrowserRecorder
from app.services.renderer import VideoRenderer, _duration
from app.services.storage import OutputStorage
from app.services.store import store
from app.services.subtitles import create_vtt
from app.services.tts import SpeechService


class VideoPipeline:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.planner = ScenarioPlanner()
        self.narration = NarrationWriter()
        self.recorder = BrowserRecorder()
        self.speech = SpeechService()
        self.renderer = VideoRenderer()
        self.storage = OutputStorage()

    async def run(self, job: VideoJob) -> None:
        base = Path(self.settings.output_dir) / job.id
        try:
            job.status = VideoJobStatus.planning
            job.add_event("Planning a demo scenario from URL and goal")
            store.save(job)

            # Render the page first so planning is grounded in what a visitor
            # actually sees (client-rendered SPAs are empty in raw HTML) and can
            # choose real on-page tabs/buttons to click.
            page_text, clickables = await self.recorder.probe(
                str(job.input.url), job.input.aspect_ratio, job.input.language
            )
            scenario = await self.planner.create_scenario(job.input, page_text, clickables)
            # Apply human/agent overrides authored before generation (WebMCP
            # collaborative workspace) so the edited title/narration is what gets
            # rendered, rather than a freshly generated script.
            if job.input.title_override:
                scenario.title = job.input.title_override
            if job.input.narration_override:
                scenario.narration = job.input.narration_override
            job.scenario = scenario
            job.add_event(f"Scenario generated: {scenario.title}")
            store.save(job)

            script = await self.narration.create_script(scenario, job.input.language)
            job.narration_script = script
            job.add_event("Narration script generated")
            store.save(job)

            # Synthesize the voice-over first so the screen recording can be paced
            # to the narration's length (the page keeps scrolling for the whole clip
            # instead of freezing after a short burst).
            job.add_event("Generating voice-over")
            store.save(job)
            audio = await self.speech.synthesize(script, job.input.language, base / "narration.wav")
            narration_seconds = _duration(audio)

            job.status = VideoJobStatus.recording
            job.add_event("Opening Chromium and recording the product workflow")
            store.save(job)
            raw_video, lead_in = await self.recorder.record(
                str(job.input.url), scenario, base, job.input.aspect_ratio, job.input.language,
                target_duration=narration_seconds,
            )
            job.add_event("Screen recording completed")
            store.save(job)

            job.status = VideoJobStatus.rendering
            # Spread the subtitles across the narration audio so they stay in sync.
            subtitle_text = create_vtt(script, base / "subtitles.vtt", narration_seconds)
            job.subtitle_vtt = subtitle_text

            job.add_event("Compositing recording and narration into MP4")
            output = self.renderer.render(raw_video, audio, base / "subtitles.vtt", base / "demo.mp4", trim_start=lead_in)
            job.video_path = str(output)
            job.video_url = await self.storage.publish(job.id, output)
            job.status = VideoJobStatus.completed
            job.add_event("Video generated successfully", "success")
            store.save(job)
        except Exception as exc:
            job.status = VideoJobStatus.failed
            job.error = f"{exc}\n{traceback.format_exc()}"
            job.add_event(f"Video generation failed: {exc}", "error")
            store.save(job)
