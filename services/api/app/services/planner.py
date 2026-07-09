from app.core.config import get_settings
from app.models.video_job import DemoScenario, VideoJobCreate


class ScenarioPlanner:
    async def create_scenario(self, request: VideoJobCreate) -> DemoScenario:
        settings = get_settings()
        if settings.ai_provider == "vertex":
            return await self._vertex_scenario(request)
        return self._mock_scenario(request)

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

    async def _vertex_scenario(self, request: VideoJobCreate) -> DemoScenario:
        # Hackathon-safe placeholder. The commercial version can replace this with
        # richer site-specific scenario generation. Keeping a deterministic fallback
        # avoids breaking the demo if Vertex credentials are unavailable.
        return self._mock_scenario(request)


class NarrationWriter:
    async def create_script(self, scenario: DemoScenario, language: str) -> str:
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
