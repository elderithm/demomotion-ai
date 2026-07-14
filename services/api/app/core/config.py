from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    # Optional Playwright storageState file (captured with `make auth-capture`) so
    # the recorder can demo pages behind a login. Never commit this file.
    auth_state_path: str | None = Field(
        default=None, validation_alias=AliasChoices("DEMOMOTION_AUTH_STATE", "AUTH_STATE_PATH")
    )
    # Pluggable providers so the engine runs credential-free by default ("demo")
    # and a hosted/commercial build can swap in cloud services:
    #   ai_provider:      demo  | vertex   (scenario + narration planning)
    #   tts_provider:     demo  | google   (voice-over synthesis)
    #   storage_provider: local | gcs      (where the MP4 is stored/served)
    ai_provider: str = "demo"
    tts_provider: str = "demo"
    storage_provider: str = "local"
    # Optional dotted path to a BrowserRecorder subclass, so a deployment
    # (e.g. the hosted/commercial edition) can plug in its own recorder.
    # Example: RECORDER_CLASS=my_package.recorder.MyRecorder
    recorder_class: str | None = None
    gcp_project_id: str | None = None
    gcp_location: str = "asia-northeast1"
    gcs_bucket: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    output_dir: str = "./generated"
    public_base_url: str = "http://localhost:8080"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
