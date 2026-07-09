from app.models.video_job import VideoJob


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, VideoJob] = {}

    def save(self, job: VideoJob) -> VideoJob:
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> VideoJob | None:
        return self._jobs.get(job_id)

    def list(self) -> list[VideoJob]:
        return sorted(self._jobs.values(), key=lambda job: job.created_at, reverse=True)


store = InMemoryJobStore()
