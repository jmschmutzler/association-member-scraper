import asyncio
from playwright.async_api import async_playwright, Page

PAGE_TIMEOUT = 30_000  # ms

NEXT_PAGE_SELECTORS = [
    "a[rel='next']",
    "a:has-text('Next')",
    "a:has-text('›')",
    "a:has-text('»')",
    "button:has-text('Next')",
    ".pagination .next:not(.disabled)",
    "[aria-label='Next page']",
    "[aria-label='next']",
]


async def _find_next_button(page: Page):
    for selector in NEXT_PAGE_SELECTORS:
        try:
            el = await page.query_selector(selector)
            if el and await el.is_visible():
                return el
        except Exception:
            continue
    return None


async def _render_with_browser(url: str, max_pages: int) -> list[str]:
    pages_html: list[str] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=PAGE_TIMEOUT, wait_until="networkidle")

        for _ in range(max_pages):
            pages_html.append(await page.content())
            next_btn = await _find_next_button(page)
            if not next_btn:
                break
            await next_btn.click()
            await page.wait_for_load_state("networkidle", timeout=PAGE_TIMEOUT)

        await browser.close()
    return pages_html


async def render_all_pages(url: str, max_pages: int = 20) -> list[str]:
    """Render a URL with Playwright and follow pagination.

    Returns a list of HTML strings (one per page).
    Retries once on any exception. Raises on second failure.
    """
    for attempt in range(2):
        try:
            return await _render_with_browser(url, max_pages)
        except Exception:
            if attempt == 1:
                raise
            await asyncio.sleep(2)
    return []
