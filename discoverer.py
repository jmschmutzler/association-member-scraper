import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

DIRECTORY_PATTERNS = [
    r"/members?(/|$)",
    r"/directory(/|$)",
    r"/find-a-member(/|$)",
    r"/our-members?(/|$)",
    r"/member-directory(/|$)",
    r"/membership-directory(/|$)",
    r"/search-members?(/|$)",
    r"/member-search(/|$)",
    r"/member-list(/|$)",
]


def _looks_like_directory(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(re.search(pattern, path) for pattern in DIRECTORY_PATTERNS)


async def discover_directory_url(url: str) -> str:
    """Return the member directory URL for the given URL.

    If the URL already looks like a directory page, return it unchanged.
    Otherwise fetch the homepage, scan internal links for directory patterns,
    and return the first match. Falls back to the original URL if nothing found.
    """
    if _looks_like_directory(url):
        return url

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            response = await client.get(url)
            response.raise_for_status()
    except Exception:
        return url

    parsed = urlparse(url)
    base_netloc = parsed.netloc
    base = f"{parsed.scheme}://{base_netloc}"
    soup = BeautifulSoup(response.text, "html.parser")

    for a in soup.find_all("a", href=True):
        href = urljoin(base, a["href"])
        if urlparse(href).netloc == base_netloc and _looks_like_directory(href):
            return href

    return url
