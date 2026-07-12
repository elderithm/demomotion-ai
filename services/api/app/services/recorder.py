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

# Headless Chromium does not paint a mouse pointer, so real clicks are invisible
# in the recording — the result just appears and the viewer never sees the button
# get pressed. Inject a synthetic cursor that follows mouse moves and can pulse on
# click, so interactions are visible on screen. Runs at document start on every
# navigation (via add_init_script).
_CURSOR = """() => {
  if (window.__dmCursorReady) return;
  window.__dmCursorReady = true;
  const ensure = () => {
    if (document.getElementById('__dm_cursor') || !document.body) return;
    const c = document.createElement('div');
    c.id = '__dm_cursor';
    Object.assign(c.style, {
      position: 'fixed', left: '0px', top: '0px', width: '20px', height: '20px',
      borderRadius: '50%', background: 'rgba(20,24,40,0.35)',
      border: '2px solid rgba(255,255,255,0.95)',
      boxShadow: '0 2px 10px rgba(0,0,0,0.45)', zIndex: '2147483647',
      pointerEvents: 'none', transform: 'translate(-50%,-50%)',
      transition: 'transform .08s ease-out',
    });
    (document.body || document.documentElement).appendChild(c);
  };
  document.addEventListener('DOMContentLoaded', ensure);
  ensure();
  document.addEventListener('mousemove', (e) => {
    const c = document.getElementById('__dm_cursor');
    if (c) { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }
  }, true);
  window.__dmClickPulse = () => {
    const c = document.getElementById('__dm_cursor');
    if (!c) return;
    c.animate(
      [{ transform: 'translate(-50%,-50%) scale(1)', background: 'rgba(102,88,255,0.5)' },
       { transform: 'translate(-50%,-50%) scale(0.55)', background: 'rgba(102,88,255,0.8)' },
       { transform: 'translate(-50%,-50%) scale(1)', background: 'rgba(20,24,40,0.35)' }],
      { duration: 320, easing: 'ease-out' }
    );
  };
}"""

# Smoothly scroll the tagged container (or the window) to a fraction [0..1] of its
# scrollable height over `dur` ms, resolving when done. Driven by rAF so the motion
# is continuous — this fills the video with movement instead of discrete jumps.
_SCROLL_ANIM = """([toFrac, dur]) => new Promise((resolve) => {
  const el = document.querySelector('[data-dm-scroll]');
  const maxY = el ? (el.scrollHeight - el.clientHeight)
                  : ((document.scrollingElement || document.documentElement).scrollHeight - window.innerHeight);
  const toY = Math.max(0, maxY) * toFrac;
  const startY = el ? el.scrollTop : window.scrollY;
  const start = performance.now();
  function step(now) {
    const t = Math.min(1, (now - start) / dur);
    const e = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;  // easeInOutQuad
    const y = startY + (toY - startY) * e;
    if (el) el.scrollTop = y; else window.scrollTo(0, y);
    if (t < 1) requestAnimationFrame(step); else resolve();
  }
  requestAnimationFrame(step);
})"""

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
        self, url: str, scenario: DemoScenario, output_dir: Path, aspect_ratio: str,
        language: str = "en-US", target_duration: float | None = None,
    ) -> tuple[Path, float]:
        output_dir.mkdir(parents=True, exist_ok=True)
        viewport = self._viewport(aspect_ratio)
        video_dir = output_dir / "raw"
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await self._context(browser, viewport, language, record_dir=video_dir)
            # Paint a visible cursor so clicks read as real interactions on screen.
            # add_init_script injects source verbatim (it does not call it like
            # evaluate does), so wrap the function as an IIFE to run it.
            await context.add_init_script(f"({_CURSOR})()")
            page = await context.new_page()
            lead_in = await _prepare(page, url)
            # Mark the start of the kept video (the blank load-in before this is
            # trimmed) so the page tour can be paced to fill the narration length.
            content_start = time.monotonic()
            await page.wait_for_timeout(1500)
            try:
                await page.evaluate(_TAG_SCROLLER)
            except Exception:
                pass

            # Show a real input→submit workflow: type into the page's primary text
            # field before clicking, so the demo reads as a user driving the product.
            await self._demo_type(page)

            # Run the planned interactions (Gemini-chosen tabs/buttons, or the demo
            # app's data-testid steps). Hold on the result afterwards rather than
            # scrolling away immediately, so a revealed result is clearly visible.
            planned = [s.get("text") or s.get("selector") for s in scenario.selectors]
            print(f"[recorder] planned actions: {planned}", flush=True)
            clicked = False
            clicks_done = 0
            for step in scenario.selectors:
                action = step.get("action")
                selector = step.get("selector")
                try:
                    if action == "click_text" and step.get("text"):
                        # Cap interactions: on content-heavy pages the clickables are
                        # tabs/links near the top, so clicking many of them just
                        # dwells at the top and buries the page tour below.
                        if clicks_done >= 2:
                            continue
                        await self._click_by_text(page, url, step["text"])
                        clicked = True
                        clicks_done += 1
                        print(f"[recorder] clicked: {step['text']!r}", flush=True)
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

            # If a click just revealed content (a launch plan, an expanded panel),
            # bring the top into view and hold so the viewer registers the result
            # before the page tour begins.
            if clicked:
                await self._hold_on_result(page, 1500)

            # Continuously scroll the whole page, paced to fill the rest of the
            # narration so the video keeps moving instead of freezing on a single
            # frame once a short scroll burst ends.
            budget = None
            if target_duration:
                budget = target_duration - (time.monotonic() - content_start) - 1.5
            await self._scroll_full(page, budget)
            await page.wait_for_timeout(1500)

            video = page.video
            await context.close()
            await browser.close()
            if video is None:
                raise RuntimeError("Playwright did not produce a video")
            return Path(await video.path()), lead_in

    async def _demo_type(self, page) -> None:
        """If the page has a single prominent text field, animate the cursor to it
        and re-type its content, so the recording shows a real input→submit flow.
        Conservative on purpose: skips multi-field forms and sensitive inputs so it
        stays safe on arbitrary sites."""
        try:
            fields = page.locator(
                "textarea, input[type=text], input[type=search], input:not([type])"
            )
            count = await fields.count()
            # 0 → nothing to type; >3 → likely a login/checkout form, leave it alone.
            if count == 0 or count > 3:
                return
            target = None
            box = None
            best_w = 0.0
            for i in range(min(count, 5)):
                el = fields.nth(i)
                if not await el.is_visible():
                    continue
                b = await el.bounding_box()
                # Only a wide field in the upper part of the page (a hero input).
                if not b or b["y"] > 520 or b["width"] < 220:
                    continue
                if b["width"] > best_w:
                    best_w, target, box = b["width"], el, b
            if target is None or box is None:
                return
            value = (await target.input_value()) or ""
            if not value.strip():
                return
            cx = box["x"] + box["width"] / 2
            cy = box["y"] + box["height"] / 2
            await page.mouse.move(cx, cy, steps=20)
            await page.wait_for_timeout(300)
            await target.click(timeout=3000)
            await page.wait_for_timeout(250)
            await target.fill("")
            await page.wait_for_timeout(250)
            await target.type(value, delay=35)
            await page.wait_for_timeout(600)
            print("[recorder] typed into primary input", flush=True)
        except Exception as exc:
            print(f"[recorder] input demo skipped: {exc!r}", flush=True)

    async def _hold_on_result(self, page, ms: int) -> None:
        """Bring the top (where inline results usually render) into view and pause,
        so freshly revealed content is clearly visible before the page tour."""
        try:
            await page.evaluate(
                "() => { const el = document.querySelector('[data-dm-scroll]');"
                " (el || window).scrollTo({ top: 0, behavior: 'smooth' }); }"
            )
        except Exception:
            pass
        await page.wait_for_timeout(ms)

    async def _scroll_full(self, page, budget: float | None = None) -> None:
        """Continuously scroll the whole page top→bottom→top, pacing the motion to
        fill `budget` seconds so the recording keeps moving for the entire narration
        instead of freezing after a short burst. Falls back to a fixed pace when no
        budget is given."""
        budget = budget if budget and budget > 4 else 16.0
        try:
            # Start from the top so the tour is complete, then glide down and back.
            await page.evaluate(_SCROLL_ANIM, [0.0, 200])
            await page.wait_for_timeout(250)
            # Spend most of the budget going down (the reveal), a bit coming back up.
            down_ms = int(budget * 1000 * 0.60)
            up_ms = int(budget * 1000 * 0.34)
            await page.evaluate(_SCROLL_ANIM, [1.0, down_ms])
            await page.wait_for_timeout(int(budget * 1000 * 0.04))
            await page.evaluate(_SCROLL_ANIM, [0.0, up_ms])
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
        await page.wait_for_timeout(500)
        # Glide the visible cursor to the target and pulse it, so the recording
        # shows the button being approached and pressed (not a result popping in).
        try:
            box = await loc.bounding_box()
            if box:
                cx = box["x"] + box["width"] / 2
                cy = box["y"] + box["height"] / 2
                await page.mouse.move(cx, cy, steps=25)
                await page.wait_for_timeout(450)
                await page.evaluate("() => window.__dmClickPulse && window.__dmClickPulse()")
                await page.wait_for_timeout(200)
        except Exception:
            pass
        try:
            await loc.click(timeout=3000)
        except Exception:
            # div[role=tab]/custom widgets with React handlers can reject a real
            # click (intercepted or never "stable"); dispatch the event directly so
            # the tab/panel still switches.
            await loc.dispatch_event("click")
        await page.wait_for_timeout(1000)
