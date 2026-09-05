import requests
from pathlib import Path

# Politeness config
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/zia0001/fastapi-task-api)"
TIMEOUT_SECONDS = 10

BASE_DIR = Path(__file__).resolve().parent.parent  # scraper/
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def fetch_page(url: str, cache_filename: str) -> str:
    """
    Fetch a page politely, or read it from cache if already saved.
    Returns the raw HTML as a string.
    """
    cache_path = CACHE_DIR / cache_filename

    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        print(f"CACHE HIT — {cache_filename} ({len(html)} bytes)")
        return html

    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)

    if response.status_code != 200:
        raise RuntimeError(f"Fetch failed: {url} returned {response.status_code}")

    html = response.text
    cache_path.write_text(html, encoding="utf-8")
    print(f"FETCH — {cache_filename} ({len(html)} bytes)")
    return html


if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/page-1.html"
    fetch_page(url, "catalogue-page-1.html")