import asyncio

from app.core.config import get_settings
from app.models.video_job import DemoScenario, VideoJobCreate


class ScenarioPlanner:
    async def create_scenario(
        self, request: VideoJobCreate, page_text: str = "", clickables: list[str] | None = None
    ) -> DemoScenario:
        settings = get_settings()
        if settings.ai_provider == "vertex":
            try:
                return await self._vertex_scenario(request, page_text, clickables or [])
            except Exception as exc:
                # Never fail the whole job on planning: fall back to the demo
                # scenario. Log the reason so the fallback is not silent (visible
                # in Cloud Run logs).
                print(f"[planner] Gemini planning failed, using demo fallback: {exc!r}", flush=True)
                return self._demo_scenario(request)
        return self._demo_scenario(request)

    async def _vertex_scenario(
        self, request: VideoJobCreate, page_text: str, clickables: list[str]
    ) -> DemoScenario:
        from app.services.gemini import GeminiPlanner

        plan = await asyncio.to_thread(GeminiPlanner().generate, request, page_text, clickables)
        # Gemini picks which on-page tabs/buttons to click by their visible text;
        # the recorder resolves them against the live DOM and clicks safely.
        selectors = [
            {"action": "click_text", "text": label} for label in plan.get("actions", [])
        ]
        return DemoScenario(
            title=plan["title"],
            steps=plan["steps"],
            selectors=selectors,
            narration=plan["narration"],
        )

    def _demo_scenario(self, request: VideoJobCreate) -> DemoScenario:
        # Deterministic scenario whose selectors match the bundled demo-app, so
        # the demo provider records a real click-through with no cloud calls.
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
