---
description: Generate a narrated demo video (mp4) of a web app from a URL and a goal
argument-hint: <url> <goal>
---

Generate a narrated demo video with the bundled generator.

Arguments provided: $ARGUMENTS

Interpret them as:
- **URL** — the first whitespace-delimited token (the web app to record).
- **Goal** — everything after the URL (free text; may contain spaces).

If the URL or the goal is missing, ask the user for it before continuing.

Then run this from the current working directory (Docker must be running):

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/generate.sh" \
  --url "<URL>" \
  --goal "<GOAL>" \
  --output ./demo.mp4
```

- **Output location**: write the MP4 into the **current working directory** (where
  the user is running Claude Code) with a relative path like `./demo.mp4`. Never
  write to `/tmp` or the plugin directory. If `./demo.mp4` already exists, pick a
  non-clobbering name (e.g. `./demo-2.mp4`).
- A local dev server works too — the script rewrites `localhost`/`127.0.0.1` so
  the container can reach the host.
- For tailored Gemini narration, add `--ai vertex --tts google --gcp-project <id>`
  (after `gcloud auth application-default login`).

When it finishes, report the absolute path to the generated file. Do not try to
play or embed it.
