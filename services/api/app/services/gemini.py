import json

from app.core.config import get_settings
from app.models.video_job import VideoJobCreate


class GeminiPlanner:
    """Generates a demo scenario and narration from the target URL, the user's
    goal, and text extracted from the page, using Vertex AI Gemini via the
    google-genai SDK."""

    def generate(self, request: VideoJobCreate, page_context: str) -> dict:
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

        prompt = f"""You are scripting a short, narrated product demo video.

Target site URL: {request.url}
What the demo should show (goal): {request.goal}
Narration language: {language_name}

Text extracted from the page:
\"\"\"
{context}
\"\"\"

Write a plan grounded in the actual page text and the goal above. Return ONLY a
JSON object with these keys:
- "title": a short demo title, at most 8 words.
- "steps": an array of 4-6 short PLAIN STRINGS (not objects) describing, in
  order, what the viewer sees on screen.
- "narration": a natural-sounding voice-over script in {language_name}, 3 to 5
  sentences. It should introduce the product, follow the stated goal, and refer
  to what is actually on the page. Plain text only, no markdown, and do not
  mention that it was AI-generated.
- "actions": an array of 0 to 3 strings, each the EXACT visible text of a button
  or link on the page to click, in order, to demonstrate the goal. Use only real
  labels you can see in the page text, prefer primary calls-to-action and
  in-site navigation, and never include anything that logs out, deletes data,
  submits a form, or leaves the site."""

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
            "actions": actions[:3],
        }
