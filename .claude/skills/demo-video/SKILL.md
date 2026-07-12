---
name: demo-video
description: Generate a narrated demo video (mp4) of a web app from its URL and a demo goal.
---

# Demo Video (in-repo)

This skill is packaged for distribution as the **`demomotion`** Claude Code plugin
(see [`plugins/demomotion/`](../../../plugins/demomotion/)). It is auto-discovered
when you run Claude Code inside this repo. The single source of truth for the
script and the full docs lives in the plugin.

## How to run

Given a URL and a goal, run the bundled script (Docker required):

```bash
plugins/demomotion/skills/demo-video/scripts/generate.sh \
  --url https://your-app.example.com \
  --goal "Explain the app for a first-time visitor, focusing on the key features." \
  --output demo.mp4
```

- Local dev servers work — pass `--url http://localhost:3000/...` (auto-rewritten to
  reach the host).
- Options and tailored-narration flags (`--ai vertex --tts google --gcp-project …`,
  after `gcloud auth application-default login`) are documented in
  [`plugins/demomotion/skills/demo-video/SKILL.md`](../../../plugins/demomotion/skills/demo-video/SKILL.md).

Report the final `.mp4` path to the user; do not try to play or embed it.
