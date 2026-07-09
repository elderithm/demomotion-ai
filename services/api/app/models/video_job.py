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


class DemoScenario(BaseModel):
    title: str
    steps: list[str]
    selectors: list[dict] = Field(default_factory=list)


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
