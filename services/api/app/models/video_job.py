from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from uuid import uuid4


class VideoJobStatus(str, Enum):
    queued = "queued"
    planning = "planning"
    recording = "recording"
    rendering = "rendering"
    completed = "completed"
    failed = "failed"


class VideoJobCreate(BaseModel):
    url: HttpUrl
    goal: str = Field(min_length=4, max_length=1200)
    language: str = Field(default="en-US")
    aspect_ratio: str = Field(default="16:9", pattern="^(16:9|9:16)$")
    # Optional human/agent-authored overrides. When supplied (e.g. from the WebMCP
    # collaborative workspace), the pipeline uses these instead of regenerating the
    # narration/title from scratch, so a demo edited before generation actually
    # affects the rendered video. Both default to None to keep existing behavior.
    title_override: str | None = Field(default=None, max_length=200)
    narration_override: str | None = Field(default=None, max_length=4000)


class DemoDraftRequest(BaseModel):
    """Lightweight planning request: produce an editable scenario + narration draft
    without recording or rendering. Reused by the WebMCP `create_demo` tool."""

    url: HttpUrl
    goal: str = Field(min_length=4, max_length=1200)
    language: str = Field(default="en-US")


class DemoDraft(BaseModel):
    title: str
    steps: list[str]
    narration: str


class DemoScenario(BaseModel):
    title: str
    steps: list[str]
    selectors: list[dict] = Field(default_factory=list)
    # Voice-over script generated together with the scenario (Gemini). Optional so
    # the deterministic/mock path can leave it unset and fall back to canned text.
    narration: str | None = None


class JobEvent(BaseModel):
    message: str
    level: str = "info"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VideoJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    status: VideoJobStatus = VideoJobStatus.queued
    input: VideoJobCreate
    scenario: DemoScenario | None = None
    narration_script: str | None = None
    subtitle_vtt: str | None = None
    video_path: str | None = None
    video_url: str | None = None
    error: str | None = None
    events: list[JobEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def add_event(self, message: str, level: str = "info") -> None:
        self.events.append(JobEvent(message=message, level=level))
        self.updated_at = datetime.now(timezone.utc)
