---
name: demo-video
description: Generate a narrated demo video (mp4) of a web app from its URL and a demo goal.
---

# Demo Video

Generate a narrated product-demo video (`.mp4`) of any web app from a **URL** and a
**goal**. A containerized pipeline opens the site with Playwright, plans a scenario,
records the screen, writes narration, adds subtitles, and encodes an MP4 — all
locally, using the public `ghcr.io/elderithm/demomotion-ai-api` image.

## When to use

The user asks to "make/record a demo video" of a web app, landing page, or a page
they just changed. They give a URL (public, a preview deploy, or a local dev server)
and what the demo should show.

## Prerequisites

- **Docker** running (the pipeline runs in a container).
- **python3** and **curl** on PATH (used to talk to the local API).
- For tailored Gemini narration only (optional): local Application Default
  Credentials — `gcloud auth application-default login`.

## How to run

Call the bundled script with the URL and goal. It prints the output path when done.
The script lives at `${CLAUDE_PLUGIN_ROOT}/skills/demo-video/scripts/generate.sh`:

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/demo-video/scripts/generate.sh" \
  --url https://your-app.example.com \
  --goal "Explain the app for a first-time visitor, focusing on the key features." \
  --output demo.mp4
```

- A **local** dev server works too — pass `--url http://localhost:3000/...`; the
  script rewrites `localhost`/`127.0.0.1` so the container can reach your host.
- Options: `--language en-US|ja-JP` (default `en-US`), `--aspect 16:9|9:16`,
  `--output PATH`, `--image REF` (defaults to the public GHCR image), `--port N`.

### Default vs tailored narration

- **Default (no credentials)** — generic narration via the `demo` providers. Nothing
  to set up.
- **Tailored (Gemini + Google TTS)** — after `gcloud auth application-default login`:

  ```bash
  "${CLAUDE_PLUGIN_ROOT}/skills/demo-video/scripts/generate.sh" \
    --url https://your-app.example.com \
    --goal "..." \
    --ai vertex --tts google --gcp-project YOUR_PROJECT_ID
  ```

## Notes

- First run pulls the API image (~a few GB) once; subsequent runs are fast.
- The script starts the container, submits the job, polls until it completes, writes
  the MP4, and always removes the container on exit.
- Report the final `.mp4` path to the user; do not try to play or embed it.
