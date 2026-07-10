from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import async_playwright

from app.models.video_job import DemoScenario


class BrowserRecorder:
    @staticmethod
    async def _click_by_text(page, base_url: str, text: str) -> None:
        """Click a button/link identified by its visible text, but only if it is
        safe: skip elements that open a new tab or navigate off-site so the demo
        stays on the target product."""
        loc = page.get_by_role("link", name=text, exact=False).or_(
            page.get_by_role("button", name=text, exact=False)
        ).first
        await loc.wait_for(state="visible", timeout=4000)
        if await loc.get_attribute("target") == "_blank":
            return
        href = await loc.get_attribute("href")
        if href and href.startswith(("http://", "https://")):
            host = urlparse(href).netloc
            if host and host != urlparse(base_url).netloc:
                return
        await loc.scroll_into_view_if_needed(timeout=3000)
        await page.wait_for_timeout(700)
        await loc.click(timeout=4000)
        # Linger so the click's result (navigation / panel) is visible on screen.
        await page.wait_for_timeout(2200)

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
                # A real UA + locale so sites don't serve a bot/blank variant.
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="ja-JP",
            )
            page = await context.new_page()
            try:
                # 'load' waits for the initial bundle without hanging like
                # 'networkidle' does on sites with video/polling/analytics. Don't
                # fail the job if navigation is slow.
                await page.goto(url, wait_until="load", timeout=45000)
            except Exception:
                pass
            # Client-rendered SPAs paint only after hydration; wait (bounded) for
            # real text to appear before recording, otherwise the video is blank.
            try:
                await page.wait_for_function(
                    "() => document.body && document.body.innerText.trim().length > 150",
                    timeout=15000,
                )
            except Exception:
                pass
            await page.wait_for_timeout(2000)
            for selector_action in scenario.selectors:
                action = selector_action.get("action")
                selector = selector_action.get("selector")
                try:
                    if action == "click_text" and selector_action.get("text"):
                        await self._click_by_text(page, url, selector_action["text"])
                    elif action == "click" and selector:
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
            # Scroll through the page so the recording is a walkthrough of the
            # content rather than a single static frame. Use JS scrolling (rather
            # than mouse.wheel, which is unreliable in headless Chromium) so the
            # viewport is guaranteed to move.
            try:
                total = await page.evaluate(
                    "() => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
                )
            except Exception:
                total = 0
            view_h = viewport["height"]
            steps = max(4, min(10, int(total / view_h) + 1)) if total else 5
            for i in range(steps):
                target = int(total * (i + 1) / steps) if total else (i + 1) * view_h
                try:
                    await page.evaluate(
                        "(y) => window.scrollTo({ top: y, behavior: 'smooth' })", target
                    )
                except Exception:
                    pass
                await page.wait_for_timeout(1300)
            try:
                await page.evaluate("() => window.scrollTo({ top: 0, behavior: 'smooth' })")
            except Exception:
                pass
            await page.wait_for_timeout(1800)
            video = page.video
            await context.close()
            await browser.close()
            if video is None:
                raise RuntimeError("Playwright did not produce a video")
            return Path(await video.path())
