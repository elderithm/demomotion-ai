from datetime import timedelta
from pathlib import Path

from app.core.config import get_settings

# How long a generated video's signed URL stays valid (V4 maximum is 7 days).
SIGNED_URL_TTL = timedelta(days=7)


class OutputStorage:
    async def publish(self, job_id: str, file_path: Path) -> str:
        settings = get_settings()
        if settings.storage_provider == "gcs" and settings.gcs_bucket:
            try:
                from google.cloud import storage

                client = storage.Client(project=settings.gcp_project_id)
                bucket = client.bucket(settings.gcs_bucket)
                blob = bucket.blob(f"videos/{job_id}/{file_path.name}")
                blob.upload_from_filename(str(file_path), content_type="video/mp4")
                return self._signed_url(blob)
            except Exception:
                # Fall back to the authenticated download endpoint if upload or
                # signing fails (e.g. missing credentials in local dev).
                pass
        return f"/v1/video-jobs/{job_id}/download"

    def _signed_url(self, blob) -> str:
        # The output bucket is private, so hand back a time-limited V4 signed URL.
        # On Cloud Run there is no key file, so sign via the IAM signBlob API using
        # the attached runtime service account's short-lived access token. This
        # needs the IAM Service Account Credentials API enabled and the runtime SA
        # to hold roles/iam.serviceAccountTokenCreator on itself.
        from google.auth import default
        from google.auth.transport.requests import Request

        credentials, _ = default()
        credentials.refresh(Request())
        return blob.generate_signed_url(
            version="v4",
            expiration=SIGNED_URL_TTL,
            method="GET",
            service_account_email=credentials.service_account_email,
            access_token=credentials.token,
        )
