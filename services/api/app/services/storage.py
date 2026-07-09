from pathlib import Path
from app.core.config import get_settings


class OutputStorage:
    async def publish(self, job_id: str, file_path: Path) -> str:
        settings = get_settings()
        if settings.gcs_bucket:
            try:
                from google.cloud import storage
                client = storage.Client(project=settings.gcp_project_id)
                bucket = client.bucket(settings.gcs_bucket)
                blob = bucket.blob(f"videos/{job_id}/{file_path.name}")
                blob.upload_from_filename(str(file_path), content_type="video/mp4")
                return f"https://storage.googleapis.com/{settings.gcs_bucket}/videos/{job_id}/{file_path.name}"
            except Exception:
                pass
        return f"/v1/video-jobs/{job_id}/download"
