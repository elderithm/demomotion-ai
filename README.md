# DemoMotion AI

**DemoMotion AI** is a hackathon MVP that turns a web app URL and a demo goal into a narrated product demo video.

This repository is published as the open-source core for the Findy hackathon. It is licensed under AGPL-3.0-or-later. A hosted commercial edition can be built separately as DemoMotion Cloud.

## What it does

1. User enters a public web app URL and a demo goal.
2. The backend generates a browser action scenario.
3. A Playwright worker opens the site and records the screen.
4. Gemini generates a narration script and subtitles.
5. Google Cloud Text-to-Speech creates narration audio.
6. ffmpeg combines screen recording, narration, and subtitles into an MP4.
7. The result is saved locally in dev or to Cloud Storage in GCP.

For hackathon reliability, the app supports `AI_PROVIDER=mock`, which generates deterministic scenarios and narration without external API calls.

## Monorepo layout

```txt
apps/
  web/       Next.js dashboard for creating video jobs and viewing results
  demo-app/  Small demo SaaS used for the hackathon recording
services/
  api/       FastAPI API + worker orchestration + Playwright/ffmpeg pipeline
infra/       Terraform for Google Cloud Run, Storage, Artifact Registry, IAM
docs/        Architecture and demo instructions
scripts/     Local helper scripts
```

## Quick start with Docker Compose

This is the recommended local setup.

### Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose v2

### Start everything

```bash
docker compose up --build
```

Or:

```bash
make compose-up
```

Open:

- Web dashboard: http://localhost:3000
- Demo app: http://localhost:3001
- API docs: http://localhost:8080/docs

The dashboard is prefilled with this internal Docker URL:

```txt
http://demo-app:3001
```

That URL is correct when the API container records the demo app. If you run the API directly on your host machine, use `http://localhost:3001` instead.

### Stop

```bash
docker compose down
```

To remove local Docker volumes as well:

```bash
docker compose down -v --remove-orphans
```

## Services in Docker Compose

```txt
web       Next.js dashboard on port 3000
api       FastAPI + Playwright + ffmpeg on port 8080
demo-app  Demo SaaS app on port 3001
```

The local Docker setup uses `AI_PROVIDER=mock`, so it does not require Gemini, Vertex AI, or Google Cloud credentials.

## Non-Docker local setup

### Prerequisites

- Node.js 20+
- pnpm 9+
- Python 3.12++
- uv or pip
- ffmpeg
- Chromium dependencies for Playwright

### Install

```bash
make install
```

### Run locally

Terminal 1:

```bash
make dev-api
```

Terminal 2:

```bash
make dev-demo
```

Terminal 3:

```bash
make dev-web
```

When running all services directly on the host, use this demo URL in the dashboard:

```txt
http://localhost:3001
```

## Environment variables

`services/api/.env.example`:

```env
APP_ENV=local
AI_PROVIDER=mock
GCP_PROJECT_ID=
GCP_LOCATION=asia-northeast1
GCS_BUCKET=
GOOGLE_APPLICATION_CREDENTIALS=
OUTPUT_DIR=./generated
PUBLIC_BASE_URL=http://localhost:8080
```

For Google Cloud / Gemini:

```env
AI_PROVIDER=vertex
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=asia-northeast1
GCS_BUCKET=your-output-bucket
```

## Hackathon demo flow

1. Start Docker Compose.
2. Open the web dashboard.
3. Keep the default URL: `http://demo-app:3001`.
4. Set goal: `Show how a founder can create a launch plan from a rough idea.`
5. Click **Generate demo video**.
6. Watch job progress.
7. Play or download the generated MP4.

## Docker notes

The API container uses the official Playwright Python image and installs ffmpeg, so Chromium recording works inside Docker. Generated files are stored in a Docker volume named `api_generated`.

## Standalone evaluation

This repository is intended to run standalone for hackathon review. The quickest path is:

```bash
docker compose up --build
```

Then open `http://localhost:3000`, keep the default URL `http://demo-app:3001`, and generate a demo video. In default `AI_PROVIDER=mock` mode, the app does not require Google Cloud credentials. It records the demo app with Playwright, generates subtitles, creates a placeholder audio track, and exports an MP4. To generate cloud TTS narration, set `AI_PROVIDER=vertex` and configure Google Cloud credentials.

## License

DemoMotion AI is licensed under AGPL-3.0-or-later. See [`LICENSE`](./LICENSE), [`NOTICE`](./NOTICE), and [`COMMERCIAL.md`](./COMMERCIAL.md).

The hosted SaaS edition should be kept in a separate private repository such as `demomotion-cloud` and may consume this repository as a git submodule or package dependency.

### Docker image Python compatibility

The API service uses `mcr.microsoft.com/playwright/python:v1.58.0-noble` and the API package declares `requires-python = ">=3.12,<3.15"`. This keeps the local Docker build on a modern Python line while avoiding accidental Python 3.10 installs.


## Docker Compose notes

The local Docker setup builds `web`, `demo-app`, and `api` as separate images.
This avoids pnpm store / `node_modules` races between the two Next.js services.

Use:

```bash
docker compose build --no-cache
docker compose up
```

URLs:

- Web dashboard: http://localhost:3000
- Demo app: http://localhost:3001
- API docs: http://localhost:8080/docs

Inside Docker, the API reaches the demo app at `http://demo-app:3001`.
The browser reaches the API at `http://localhost:8080`.

If you previously ran an older Compose file that mounted shared `node_modules`, clean volumes first:

```bash
docker compose down -v
docker compose build --no-cache
docker compose up
```
