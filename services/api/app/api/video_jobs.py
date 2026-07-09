from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

from app.models.video_job import VideoJob, VideoJobCreate
from app.services.store import store
from app.workers.video_pipeline import VideoPipeline

router = APIRouter(prefix="/v1/video-jobs", tags=["video-jobs"])


@router.post("", response_model=VideoJob)
async def create_video_job(payload: VideoJobCreate, background_tasks: BackgroundTasks) -> VideoJob:
    job = VideoJob(input=payload)
    job.add_event("Video job queued")
    store.save(job)
    background_tasks.add_task(VideoPipeline().run, job)
    return job


@router.get("", response_model=list[VideoJob])
async def list_video_jobs() -> list[VideoJob]:
    return store.list()


@router.get("/{job_id}", response_model=VideoJob)
async def get_video_job(job_id: str) -> VideoJob:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/download")
async def download_video(job_id: str) -> FileResponse:
    job = store.get(job_id)
    if job is None or not job.video_path:
        raise HTTPException(status_code=404, detail="Video not found")
    path = Path(job.video_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Video file missing")
    return FileResponse(path, media_type="video/mp4", filename=f"demomotion-{job_id}.mp4")


@router.get("/{job_id}/subtitles.vtt")
async def subtitles(job_id: str) -> PlainTextResponse:
    job = store.get(job_id)
    if job is None or not job.subtitle_vtt:
        raise HTTPException(status_code=404, detail="Subtitles not found")
    return PlainTextResponse(job.subtitle_vtt, media_type="text/vtt")
