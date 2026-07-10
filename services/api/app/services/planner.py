import asyncio
import re
import urllib.request

from app.core.config import get_settings
from app.models.video_job import DemoScenario, VideoJobCreate


def _fetch_page_text(url: str) -> str:
    """Best-effort fetch of the page's visible text to ground the Gemini prompt.
    Server-rendered/marketing pages yield useful text; JS-only SPAs may not, in
    which case Gemini still has the URL and goal to work from."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (compatible; DemoMotionBot/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read(300_000).decode("utf-8", "ignore")
    except Exception:
        return ""
    html = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


class ScenarioPlanner:
    async def create_scenario(self, request: VideoJobCreate) -> DemoScenario:
        settings = get_settings()
        if settings.ai_provider == "vertex":
            try:
                return await self._vertex_scenario(request)
            except Exception as exc:
                # Never fail the whole job on planning: fall back to a
                # deterministic scenario. Log the reason so the fallback is not
                # silent (visible in Cloud Run logs).
                print(f"[planner] Gemini planning failed, using fallback: {exc!r}", flush=True)
                return self._mock_scenario(request)
        return self._mock_scenario(request)

    async def _vertex_scenario(self, request: VideoJobCreate) -> DemoScenario:
        from app.services.gemini import GeminiPlanner

        page_text = await asyncio.to_thread(_fetch_page_text, str(request.url))
        plan = await asyncio.to_thread(GeminiPlanner().generate, request, page_text)
        # Gemini suggests which buttons/links to click by their visible text; the
        # recorder resolves them against the live DOM and clicks safely.
        selectors = [
            {"action": "click_text", "text": label} for label in plan.get("actions", [])
        ]
        return DemoScenario(
            title=plan["title"],
            steps=plan["steps"],
            selectors=selectors,
            narration=plan["narration"],
        )

    def _mock_scenario(self, request: VideoJobCreate) -> DemoScenario:
        return DemoScenario(
            title="Founder launch plan in under a minute",
            steps=[
                "Open the product homepage and introduce the value proposition.",
                "Click Get started to begin the workflow.",
                "Type a rough startup idea into the idea input.",
                "Click Create plan and wait for the generated launch plan.",
                "Highlight the positioning, launch channel, and first offer cards.",
            ],
            selectors=[
                {"action": "click", "selector": "[data-testid='get-started']", "description": "Open the workflow"},
                {"action": "fill", "selector": "[data-testid='idea-input']", "value": "Launch an AI demo video generator for indie hackers", "description": "Enter a product idea"},
                {"action": "click", "selector": "[data-testid='create-plan']", "description": "Generate the launch plan"},
                {"action": "wait", "selector": "[data-testid='launch-plan']", "description": "Wait for the result"},
            ],
        )


class NarrationWriter:
    async def create_script(self, scenario: DemoScenario, language: str) -> str:
        # Prefer the narration generated with the scenario (Gemini). Fall back to
        # a canned script only when it is absent (mock / offline path).
        if scenario.narration:
            return scenario.narration
        if language == "ja-JP":
            return (
                "簡単なアイデアから、ローンチ計画を作成します。\n"
                "まず、プロダクトのトップページを開き、アイデアを入力します。\n"
                "AIがポジショニング、ローンチチャネル、最初のオファーを整理します。\n"
                "チームは編集作業に時間を使わず、すぐに公開準備へ進めます。"
            )
        return (
            "Turn a rough product idea into a launch plan in seconds.\n"
            "DemoMotion AI opens the app, follows the key workflow, and captures the moment value appears on screen.\n"
            "The result is a narrated product demo your team can share on launch day."
        )
