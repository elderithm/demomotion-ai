import json

from app.core.config import get_settings
from app.models.video_job import VideoJobCreate


class GeminiPlanner:
    """Generates a demo scenario and narration from the target URL, the user's
    goal, and text extracted from the page, using Vertex AI Gemini via the
    google-genai SDK."""

    def generate(self, request: VideoJobCreate, page_context: str, clickables: list[str] | None = None) -> dict:
        settings = get_settings()
        from google import genai
        from google.genai import types

        client = genai.Client(
            vertexai=True,
            project=settings.gcp_project_id,
            location=settings.gcp_location,
        )

        language_name = "Japanese" if request.language.startswith("ja") else "English"
        context = (page_context or "").strip()[:4000] or "(no readable page text was extracted)"
        labels = [c for c in (clickables or []) if c][:25]
        clickable_block = "\n".join(f"- {c}" for c in labels) or "(none detected)"

        prompt = f"""You are scripting a short, narrated product demo video.

Target site URL: {request.url}
What the demo should show (goal): {request.goal}
Narration language: {language_name}

Text extracted from the rendered page:
\"\"\"
{context}
\"\"\"

Clickable elements on the page (tabs / buttons / links), by their exact visible label:
{clickable_block}

Write a plan grounded in the actual page content and the goal above. Return ONLY
a JSON object with these keys:
- "title": a short demo title, at most 8 words.
- "steps": an array of 4-6 short PLAIN STRINGS (not objects) describing, in
  order, what the viewer sees on screen.
- "narration": a natural-sounding voice-over script in {language_name}, 3 to 5
  sentences. It should introduce the product, follow the stated goal, and refer
  to what is actually on the page. Plain text only, no markdown, and do not
  mention that it was AI-generated.
- "actions": choose 2 to 4 items from the "Clickable elements" list to click
  through, in order, giving a guided tour so the viewer sees the product actually
  respond. Copy each label EXACTLY as written above. INCLUDE the page's primary
  call-to-action buttons (e.g. "Get started", "Create plan", "Generate", "Try it",
  "Show more") — clicking them reveals or generates on-page content, which is
  exactly what a demo should show. If the page has section tabs (overview,
  schedule, rules, FAQ), also spread picks across DIFFERENT tabs. Prefer buttons
  that produce a visible result on the same page over ones already open by default.
  Only EXCLUDE actions that are irreversible or leave the product: log out, delete,
  make a payment/purchase, or navigate to another site. A button that just shows a
  result, opens a panel, or advances a form is fine to click. Return an empty array
  only if there are genuinely no useful things to click."""

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.6,
                max_output_tokens=2048,
                # gemini-2.5 models reason with "thinking" tokens that draw from
                # the output budget; left on, a small budget is spent entirely on
                # thinking and the response text comes back empty. Disable it for
                # this structured JSON task.
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        if not response.text:
            reason = response.candidates[0].finish_reason if response.candidates else "unknown"
            raise ValueError(f"Gemini returned no text (finish_reason={reason})")
        data = json.loads(response.text)
        title = str(data.get("title") or "Product demo").strip()
        steps: list[str] = []
        for step in data.get("steps", []):
            if isinstance(step, dict):
                step = step.get("step") or step.get("heading") or step.get("text") or ""
            step = str(step).strip()
            if step:
                steps.append(step)
        narration = str(data.get("narration") or "").strip()
        if not narration:
            raise ValueError("Gemini returned an empty narration")
        actions: list[str] = []
        for action in data.get("actions", []):
            if isinstance(action, dict):
                action = action.get("label") or action.get("text") or ""
            action = str(action).strip()
            if action:
                actions.append(action)
        return {
            "title": title,
            "steps": steps or [title],
            "narration": narration,
            "actions": actions[:4],
        }
