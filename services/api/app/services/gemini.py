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
- "steps": an array of 4-6 short strings describing, in order, what the viewer
  sees on screen.
- "narration": a natural-sounding voice-over script in {language_name}, 3 to 5
  sentences. It should introduce the product, follow the stated goal, and refer
  to what is actually on the page. Plain text only, no markdown, and do not
  mention that it was AI-generated."""

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.6,
                max_output_tokens=1024,
            ),
        )
        data = json.loads(response.text)
        title = str(data.get("title") or "Product demo").strip()
        steps = [str(s).strip() for s in data.get("steps", []) if str(s).strip()]
        narration = str(data.get("narration") or "").strip()
        if not narration:
            raise ValueError("Gemini returned an empty narration")
        return {"title": title, "steps": steps or [title], "narration": narration}
