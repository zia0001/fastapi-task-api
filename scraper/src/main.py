import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
    page_url = "https://books.toscrape.com/catalogue/page-1.html"
    all_book_urls = []
    pages_visited = 0

    while page_url and pages_visited < 3:
        cache_filename = f"catalogue-page-{pages_visited + 1}.html"
        html = fetch_page(page_url, cache_filename)
        pages_visited += 1

        soup = BeautifulSoup(html, "html.parser")
        book_links = soup.select("h3 a")

        page_book_urls = [urljoin(page_url, link["href"]) for link in book_links]
        all_book_urls.extend(page_book_urls)

        next_link = soup.select_one("li.next a")
        page_url = urljoin(page_url, next_link["href"]) if next_link else None

    unique_urls = list(dict.fromkeys(all_book_urls))  # removes duplicates, keeps order

    print(f"catalogue_pages={pages_visited}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")