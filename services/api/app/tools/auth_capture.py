"""Capture a logged-in browser session as a Playwright storageState file.

Run this on your own machine — a real browser window opens. Log in to the site,
then press Enter in the terminal. The saved state lets the recorder demo pages
that require authentication, without ever handling your credentials:

    make auth-capture URL=https://your-app.example.com
    # then, with the state file present, generate as usual:
    docker compose up

The output (default: auth/state.json) contains session cookies — treat it as a
secret and never commit it (auth/*.json is gitignored).
"""
import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def capture(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        print(
            "\nA browser window opened. Log in to the site, then press Enter here "
            "to save the session...",
            flush=True,
        )
        await asyncio.get_event_loop().run_in_executor(None, input)
        await context.storage_state(path=str(out))
        await browser.close()
    print(f"Saved login state to {out}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture a logged-in session as a Playwright storageState file."
    )
    parser.add_argument("--url", required=True, help="URL of the site to log into")
    parser.add_argument("--out", default="auth/state.json", help="Where to write the storageState JSON")
    args = parser.parse_args()
    asyncio.run(capture(args.url, Path(args.out)))


if __name__ == "__main__":
    main()
