from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    ai_provider: str = "mock"
    gcp_project_id: str | None = None
    gcp_location: str = "asia-northeast1"
    gcs_bucket: str | None = None
    output_dir: str = "./generated"
    public_base_url: str = "http://localhost:8080"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
