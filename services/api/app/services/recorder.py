import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import async_playwright

from app.core.config import get_settings
from app.models.video_job import DemoScenario

# Find the element that actually scrolls (Notion and many apps scroll an inner
# div, not the window) and tag it so later steps can address it reliably.
_TAG_SCROLLER = """() => {
  const els = [...document.querySelectorAll('*')].filter((e) => {
    const s = getComputedStyle(e);
    return (s.overflowY === 'auto' || s.overflowY === 'scroll') && e.scrollHeight > e.clientHeight + 80;
  }).sort((a, b) => b.scrollHeight - a.scrollHeight);
  if (els[0]) els[0].setAttribute('data-dm-scroll', '1');
  return !!els[0];
}"""

# Visible labels of clickable elements (tabs, buttons, links) for the planner.
_CLICKABLES = """() => {
  const out = [], seen = new Set();
  for (const e of document.querySelectorAll('a,button,[role=tab],[role=button]')) {
    const t = (e.innerText || '').trim();
    if (!t || t.length > 24 || seen.has(t)) continue;
    const r = e.getBoundingClientRect();
    if (r.width < 8 || r.height < 8) continue;
    seen.add(t);
    out.push(t);
    if (out.length >= 25) break;
  }
  return out;
}"""


async def _prepare(page, url: str) -> float:
    """Navigate and wait for a client-rendered page to actually paint. Returns the
    seconds spent (the blank load-in), so recordings can trim it later."""
    started = time.monotonic()
    try:
        # 'load' waits for the bundle without hanging like 'networkidle' does on
        # sites with video/polling/analytics. Don't fail the job if it is slow.
        await page.goto(url, wait_until="load", timeout=45000)
    except Exception:
        pass
    try:
        await page.wait_for_function(
            "() => document.body && document.body.innerText.trim().length > 150",
            timeout=15000,
        )
    except Exception:
        pass
    return time.monotonic() - started


class BrowserRecorder:
    def _viewport(self, aspect_ratio: str) -> dict:
        return {"width": 1280, "height": 720} if aspect_ratio == "16:9" else {"width": 720, "height": 1280}

    @staticmethod
    def _locale(language: str) -> str:
        # Match the browser locale to the narration language so sites that render
        # per navigator.language show the SAME language we narrate (and so the
        # labels probe extracts for the planner match the DOM we later record).
        return language if language and "-" in language else (language or "en-US")

    async def _context(self, browser, viewport: dict, language: str, record_dir: Path | None = None):
        # Derive the UA from the bundled Chromium and drop "Headless": a real,
        # current version keeps bot filters happy and stops version-gated sites
        # (e.g. Notion) from redirecting us to an "unsupported browser" page.
        seed = await browser.new_context()
        default_ua = await (await seed.new_page()).evaluate("() => navigator.userAgent")
        await seed.close()
        kwargs = {
            "viewport": viewport,
            "user_agent": default_ua.replace("HeadlessChrome", "Chrome"),
            "locale": self._locale(language),
        }
        # Reuse a captured login session (Playwright storageState) so authenticated
        # pages can be recorded. Ignored if the file is absent.
        auth_state = get_settings().auth_state_path
        if auth_state and Path(auth_state).exists():
            kwargs["storage_state"] = auth_state
        if record_dir is not None:
            kwargs["record_video_dir"] = str(record_dir)
            kwargs["record_video_size"] = viewport
        return await browser.new_context(**kwargs)

    async def probe(self, url: str, aspect_ratio: str, language: str = "en-US") -> tuple[str, list[str]]:
        """Render the page (no recording) and return its visible text plus the
        labels of clickable elements, so the planner can ground the narration and
        pick real on-page tabs/buttons to click."""
        viewport = self._viewport(aspect_ratio)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await self._context(browser, viewport, language)
            page = await context.new_page()
            await _prepare(page, url)
            # Let client-side reconciliation settle (e.g. apps that switch language
            # from navigator.language after mount) so the labels we extract match
            # the DOM the recording will later interact with. Mirrors record()'s
            # settle wait below.
            await page.wait_for_timeout(1500)
            try:
                text = await page.evaluate(
                    "() => document.body ? document.body.innerText.trim().slice(0, 4000) : ''"
                )
            except Exception:
                text = ""
            try:
                clickables = await page.evaluate(_CLICKABLES)
            except Exception:
                clickables = []
            await context.close()
            await browser.close()
            return text, clickables

    async def record(
        self, url: str, scenario: DemoScenario, output_dir: Path, aspect_ratio: str, language: str = "en-US"
    ) -> tuple[Path, float]:
        output_dir.mkdir(parents=True, exist_ok=True)
        viewport = self._viewport(aspect_ratio)
        video_dir = output_dir / "raw"
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await self._context(browser, viewport, language, record_dir=video_dir)
            page = await context.new_page()
            lead_in = await _prepare(page, url)
            await page.wait_for_timeout(1500)
            try:
                await page.evaluate(_TAG_SCROLLER)
            except Exception:
                pass

            # Run the planned interactions (Gemini-chosen tabs/buttons, or the demo
            # app's data-testid steps), scrolling through the result of each click.
            planned = [s.get("text") or s.get("selector") for s in scenario.selectors]
            print(f"[recorder] planned actions: {planned}", flush=True)
            clicked = False
            for step in scenario.selectors:
                action = step.get("action")
                selector = step.get("selector")
                try:
                    if action == "click_text" and step.get("text"):
                        await self._click_by_text(page, url, step["text"])
                        clicked = True
                        print(f"[recorder] clicked: {step['text']!r}", flush=True)
                        # Small reveal near the click; the full traversal below is
                        # what guarantees the whole page is shown.
                        await self._scroll_through(page, steps=2)
                    elif action == "click" and selector:
                        await page.locator(selector).first.click(timeout=4000)
                        await page.wait_for_timeout(900)
                    elif action == "fill" and selector:
                        await page.locator(selector).first.fill(step.get("value", ""), timeout=4000)
                        await page.wait_for_timeout(900)
                    elif action == "wait" and selector:
                        await page.locator(selector).first.wait_for(timeout=4000)
                        await page.wait_for_timeout(1500)
                except Exception as exc:
                    # Best-effort: a planned target may not exist on an arbitrary
                    # site. Skip it and keep recording rather than failing the job.
                    print(f"[recorder] action skipped ({action} {step.get('text') or selector!r}): {exc!r}", flush=True)
                    continue

            # Deterministically page through the ENTIRE page top→bottom so the
            # recording always demonstrates scrolling — regardless of whether
            # clicks left us near the top or bottom.
            await self._scroll_full(page)
            await page.wait_for_timeout(1500)

            video = page.video
            await context.close()
            await browser.close()
            if video is None:
                raise RuntimeError("Playwright did not produce a video")
            return Path(await video.path()), lead_in

    async def _scroll_through(self, page, steps: int) -> None:
        try:
            info = await page.evaluate("""() => {
              const el = document.querySelector('[data-dm-scroll]');
              return {
                total: el ? el.scrollHeight : document.documentElement.scrollHeight,
                cur: el ? el.scrollTop : window.scrollY,
                has: !!el,
              };
            }""")
        except Exception:
            return
        span = max(0, info["total"] - info["cur"])
        for i in range(steps):
            y = info["cur"] + span * (i + 1) / steps
            try:
                if info["has"]:
                    await page.evaluate(
                        "(y) => { const el = document.querySelector('[data-dm-scroll]');"
                        " if (el) el.scrollTo({ top: y, behavior: 'smooth' }); }", y
                    )
                else:
                    await page.evaluate("(y) => window.scrollTo({ top: y, behavior: 'smooth' })", y)
            except Exception:
                pass
            await page.wait_for_timeout(1200)

    async def _scroll_full(self, page) -> None:
        """Page through the entire scrollable content top→bottom, holding at each
        stop, then return to the top. Viewport-based paging (not a fixed step
        count) guarantees every section is shown on tall pages regardless of the
        current scroll position."""
        try:
            m = await page.evaluate("""() => {
              const el = document.querySelector('[data-dm-scroll]');
              return {
                total: el ? el.scrollHeight : document.documentElement.scrollHeight,
                view: el ? el.clientHeight : window.innerHeight,
                has: !!el,
              };
            }""")
        except Exception:
            return
        total, view, has = m["total"], m["view"], m["has"]
        await self._scroll_to(page, 0, has)
        await page.wait_for_timeout(900)
        step = max(1, int(view * 0.85))
        y = 0
        # Cap the stops so a very tall page can't run the recording forever.
        for _ in range(12):
            if y + view >= total:
                break
            y += step
            await self._scroll_to(page, y, has)
            await page.wait_for_timeout(1100)
        # Hold at the bottom, then glide back to the top for the closing frame.
        await self._scroll_to(page, max(0, total - view), has)
        await page.wait_for_timeout(1100)
        await self._scroll_to(page, 0, has)
        await page.wait_for_timeout(1200)

    async def _scroll_to(self, page, y: float, has: bool) -> None:
        try:
            if has:
                await page.evaluate(
                    "(y) => { const el = document.querySelector('[data-dm-scroll]');"
                    " if (el) el.scrollTo({ top: y, behavior: 'smooth' }); }", y
                )
            else:
                await page.evaluate("(y) => window.scrollTo({ top: y, behavior: 'smooth' })", y)
        except Exception:
            pass

    @staticmethod
    async def _click_by_text(page, base_url: str, text: str) -> None:
        """Click a tab/link/button identified by its visible text, but only if it
        is safe: skip elements that open a new tab or navigate off-site so the demo
        stays on the target product."""
        loc = page.get_by_role("tab", name=text, exact=False).or_(
            page.get_by_role("link", name=text, exact=False)
        ).or_(
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
        await page.wait_for_timeout(600)
        try:
            await loc.click(timeout=3000)
        except Exception:
            # div[role=tab]/custom widgets with React handlers can reject a real
            # click (intercepted or never "stable"); dispatch the event directly so
            # the tab/panel still switches.
            await loc.dispatch_event("click")
        await page.wait_for_timeout(1800)
