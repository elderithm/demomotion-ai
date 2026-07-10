from pathlib import Path
from playwright.async_api import async_playwright
from app.models.video_job import DemoScenario


class BrowserRecorder:
    async def record(self, url: str, scenario: DemoScenario, output_dir: Path, aspect_ratio: str) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        viewport = {"width": 1280, "height": 720} if aspect_ratio == "16:9" else {"width": 720, "height": 1280}
        video_dir = output_dir / "raw"
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context(
                viewport=viewport,
                record_video_dir=str(video_dir),
                record_video_size=viewport,
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=45000)
            await page.wait_for_timeout(1000)
            for selector_action in scenario.selectors:
                action = selector_action.get("action")
                selector = selector_action.get("selector")
                try:
                    if action == "click" and selector:
                        await page.locator(selector).first.click(timeout=4000)
                        await page.wait_for_timeout(900)
                    elif action == "fill" and selector:
                        await page.locator(selector).first.fill(selector_action.get("value", ""), timeout=4000)
                        await page.wait_for_timeout(900)
                    elif action == "wait" and selector:
                        await page.locator(selector).first.wait_for(timeout=4000)
                        await page.wait_for_timeout(1500)
                except Exception:
                    # Best-effort: a planned selector may not exist on an arbitrary
                    # site. Skip the step and keep recording rather than failing the
                    # whole job.
                    continue
            await page.wait_for_timeout(1800)
            video = page.video
            await context.close()
            await browser.close()
            if video is None:
                raise RuntimeError("Playwright did not produce a video")
            return Path(await video.path())
