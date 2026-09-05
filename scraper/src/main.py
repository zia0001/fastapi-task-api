import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
import time
import json

from pydantic import BaseModel, HttpUrl
from typing import Optional


class Book(BaseModel):
    title: str
    product_url: HttpUrl
    price_gbp: float
    price_text: str
    availability_text: str
    rating_text: str
    description: Optional[str] = None
    source_page: str
    fetched_at: str


# Politeness config
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/zia0001/fastapi-task-api)"
TIMEOUT_SECONDS = 10

BASE_DIR = Path(__file__).resolve().parent.parent  # scraper/
CACHE_DIR = BASE_DIR / "cache"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def fetch_page(url: str, cache_filename: str) -> str:
    """
    Fetch a page politely, or read it from cache if already saved.
    Retries once on timeout or 5xx server errors. Never retries 404/403.
    Returns the raw HTML as a string.
    """
    cache_path = CACHE_DIR / cache_filename

    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        print(f"CACHE HIT — {cache_filename} ({len(html)} bytes)")
        return html

    headers = {"User-Agent": USER_AGENT}

    for attempt in (1, 2):  # try up to twice
        try:
            response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
        except requests.exceptions.Timeout:
            if attempt == 2:
                raise RuntimeError(f"Fetch failed: {url} timed out twice")
            print(f"Timeout on {url}, retrying...")
            continue

        if response.status_code == 200:
            break  # success, exit the retry loop

        if response.status_code in (404, 403):
            raise RuntimeError(f"Fetch failed: {url} returned {response.status_code} (not retrying)")

        if response.status_code >= 500 and attempt == 1:
            print(f"Server error {response.status_code} on {url}, retrying...")
            continue

        raise RuntimeError(f"Fetch failed: {url} returned {response.status_code}")

    response.encoding = "utf-8"
    html = response.text
    cache_path.write_text(html, encoding="utf-8")
    print(f"FETCH — {cache_filename} ({len(html)} bytes)")
    return html


def clean_price(price_text: str) -> float:
    """
    Turn '£51.77' into 51.77
    """
    cleaned = price_text.replace("£", "").strip()
    return float(cleaned)


def extract_book(book_url: str, source_page: str, cache_filename: str) -> dict:
    """
    Fetch a single book page and extract its raw record (8 fields).
    """
    html = fetch_page(book_url, cache_filename)
    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("div.product_main h1").text
    price_text = soup.select_one("p.price_color").text
    availability_text = soup.select_one("p.instock.availability").text.strip()

    rating_tag = soup.select_one("p.star-rating")
    rating_text = rating_tag["class"][1]

    desc_tag = soup.select_one("#product_description")
    description = desc_tag.find_next_sibling("p").text if desc_tag else None

    return {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    run_start = datetime.now(timezone.utc)
    cache_hits = 0

    # --- Stage 2: discover 3 catalogue pages ---
    page_url = "https://books.toscrape.com/catalogue/page-1.html"
    all_book_urls = []
    pages_visited = 0

    while page_url and pages_visited < 3:
        cache_filename = f"catalogue-page-{pages_visited + 1}.html"
        if (CACHE_DIR / cache_filename).exists():
            cache_hits += 1
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

    # --- Stage 5 test: inject one deliberately broken URL ---
    unique_urls.append(
        "https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html"
    )

    # --- Stage 3: extract all books (including the fake one, which will fail) ---
    all_records = []
    failed_pages = []

    for i, book_url in enumerate(unique_urls, start=1):
        cache_filename = f"book-{i:03d}.html"
        was_cached = (CACHE_DIR / cache_filename).exists()
        if was_cached:
            cache_hits += 1

        try:
            record = extract_book(
                book_url,
                source_page="https://books.toscrape.com/catalogue/page-1.html",
                cache_filename=cache_filename,
            )
            all_records.append(record)
        except Exception as e:
            print(f"FAILED — {book_url} ({e})")
            failed_pages.append({"url": book_url, "reason": str(e)})

        if not was_cached:
            time.sleep(0.5)  # be polite — only delay for real network fetches

    print(f"detail_pages={len(all_records)}")

    # --- Stage 4: validate and store ---
    valid_books = []
    errors = []

    for raw in all_records:
        try:
            price_gbp = clean_price(raw["price_text"])
            book = Book(
                title=raw["title"],
                product_url=raw["product_url"],
                price_gbp=price_gbp,
                price_text=raw["price_text"],
                availability_text=raw["availability_text"],
                rating_text=raw["rating_text"],
                description=raw["description"],
                source_page=raw["source_page"],
                fetched_at=raw["fetched_at"],
            )
            valid_books.append(book)
        except Exception as e:
            errors.append({"record": raw, "reason": str(e)})

    # De-duplicate by canonical URL (product_url), keep first occurrence
    seen_urls = set()
    unique_books = []
    for book in valid_books:
        url_str = str(book.product_url)
        if url_str not in seen_urls:
            seen_urls.add(url_str)
            unique_books.append(book)

    with open(OUTPUT_DIR / "books.json", "w", encoding="utf-8") as f:
        json.dump(
            [b.model_dump(mode="json") for b in unique_books],
            f,
            indent=2,
            ensure_ascii=False,
        )

    with open(OUTPUT_DIR / "errors.json", "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2, ensure_ascii=False)

    print(f"valid_records={len(unique_books)}")
    print(f"invalid_records={len(errors)}")

    # --- Stage 5: write the run report ---
    run_end = datetime.now(timezone.utc)
    duration_seconds = (run_end - run_start).total_seconds()

    run_report = {
        "start_time": run_start.isoformat(),
        "duration_seconds": duration_seconds,
        "pages_fetched": pages_visited,
        "cache_hits": cache_hits,
        "valid_records": len(unique_books),
        "invalid_records": len(errors),
        "failed_pages": len(failed_pages),
        "failed_page_details": failed_pages,
    }

    with open(OUTPUT_DIR / "run-report.json", "w", encoding="utf-8") as f:
        json.dump(run_report, f, indent=2, ensure_ascii=False)

    print(f"failed_pages={len(failed_pages)}")