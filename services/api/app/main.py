from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.video_jobs import router as video_jobs_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="DemoMotion AI API",
    description="AI agent that turns a web app URL into a narrated demo video.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video_jobs_router)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "demomotion-api"}
