<div align="center">

# DemoMotion AI

**Turn a web app URL and a demo goal into a narrated product demo video.**

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/License-AGPL--3.0--or--later-blue.svg)](./LICENSE)
![Status](https://img.shields.io/badge/status-MVP-orange.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

![Next.js 16](https://img.shields.io/badge/Next.js-16-black?logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.12-009688?logo=fastapi&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-recording-2EAD33?logo=playwright&logoColor=white)
![ffmpeg](https://img.shields.io/badge/ffmpeg-encoding-007808?logo=ffmpeg&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-narration-8E75B2?logo=googlegemini&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Run%20%7C%20Vertex%20AI-4285F4?logo=googlecloud&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

<br>

![DemoMotion AI demo](demo.gif)

</div>

**DemoMotion AI** turns a web app URL and a demo goal into a narrated product demo video.

This repository is the open-source core, licensed under AGPL-3.0-or-later. A hosted commercial edition can be built separately as DemoMotion Cloud.

## What it does

1. User enters a public web app URL and a demo goal.
2. The backend generates a browser action scenario.
3. A Playwright worker opens the site and records the screen.
4. Gemini generates a narration script and subtitles.
5. Google Cloud Text-to-Speech creates narration audio.
6. ffmpeg combines screen recording, narration, and subtitles into an MP4.
7. The result is saved locally in dev or to Cloud Storage in GCP.

The app also supports `AI_PROVIDER=mock`, which generates deterministic scenarios and narration without external API calls — useful for local development and CI without Google Cloud credentials.

## Monorepo layout

```txt
apps/
  web/       Next.js dashboard for creating video jobs and viewing results
services/
  api/       FastAPI API + worker orchestration + Playwright/ffmpeg pipeline
infra/       Terraform for Google Cloud Run, Storage, Artifact Registry, IAM
docs/        Architecture notes
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
- API docs: http://localhost:8080/docs

In the dashboard, enter the public URL of the web app you want to record and a demo goal, then generate the video.

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
web  Next.js dashboard on port 3000
api  FastAPI + Playwright + ffmpeg on port 8080
```

The local Docker setup uses `AI_PROVIDER=mock`, so it does not require Gemini, Vertex AI, or Google Cloud credentials.

## Non-Docker local setup

### Prerequisites

- Node.js 20+
- pnpm 9+
- Python 3.12+
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
make dev-web
```

Then open http://localhost:3000 and enter the URL of the web app you want to record.

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

## Usage flow

1. Start Docker Compose (or the local services).
2. Open the web dashboard at http://localhost:3000.
3. Enter the public URL of the web app you want to record.
4. Set a goal, e.g. `Show how a founder can create a launch plan from a rough idea.`
5. Click **Generate demo video**.
6. Watch job progress.
7. Play or download the generated MP4.

## Docker notes

The API container uses the official Playwright Python image and installs ffmpeg, so Chromium recording works inside Docker. Generated files are stored in a Docker volume named `api_generated`.

In default `AI_PROVIDER=mock` mode, the app does not require Google Cloud credentials: it records the target site with Playwright, generates subtitles, creates a placeholder audio track, and exports an MP4. To generate cloud TTS narration, set `AI_PROVIDER=vertex` and configure Google Cloud credentials.

### Docker image Python compatibility

The API service uses `mcr.microsoft.com/playwright/python:v1.58.0-noble` and the API package declares `requires-python = ">=3.12,<3.15"`. This keeps the local Docker build on a modern Python line while avoiding accidental Python 3.10 installs.

### Rebuilding

If you previously ran an older Compose file that mounted shared `node_modules`, clean volumes first:

```bash
docker compose down -v
docker compose build --no-cache
docker compose up
```

## License

DemoMotion AI is licensed under AGPL-3.0-or-later. See [`LICENSE`](./LICENSE), [`NOTICE`](./NOTICE), and [`COMMERCIAL.md`](./COMMERCIAL.md).

The hosted SaaS edition should be kept in a separate private repository such as `demomotion-cloud` and may consume this repository as a git submodule or package dependency.
