# Architecture

DemoMotion AI is intentionally small, but the flow mirrors a production SaaS.

```txt
Next.js dashboard
  -> FastAPI /v1/video-jobs
    -> ScenarioPlanner, NarrationWriter
    -> Playwright BrowserRecorder
    -> Google Cloud Text-to-Speech or local placeholder audio
    -> ffmpeg VideoRenderer
    -> Cloud Storage or local download endpoint
```

## Why this is an AI agent

The system does not just edit uploaded footage. It plans a product story, chooses browser actions, executes the demo flow, records the UI, writes narration, and renders an output asset. By default, scenario generation runs in deterministic mock mode for reliable local development. Setting `AI_PROVIDER=vertex` is the extension point for Gemini-powered scenario planning and narration.

## Public repository boundary

This public version includes the minimal working pipeline. Commercial templates, success-rate tuning, user accounts, billing, and production prompt libraries are intentionally left out.
