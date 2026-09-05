# The Polite Scraper — Books to Scrape

A small, polite scraping pipeline that downloads the first three catalogue pages of Books to Scrape, visits all 60 book pages, turns messy HTML into clean, validated JSON records, survives a broken page without crashing, and ends every run with an honest report of what happened.

## Target classification

- **Site**: books.toscrape.com
- **Why this site**: It is an explicit public sandbox built for scraping practice.
  Per toscrape.com, the Books site is described as "desperately wants to be
  scraped" — a safe place for beginners learning web scraping and developers
  validating scraping tools.
- **Scope**: First 3 catalogue pages only (of the site's full ~50 pages / 1000 books),
  discovering all books linked from those 3 pages (60 books).
- **Data collected**: title, product URL, price, availability, star rating,
  description, source page, fetch timestamp — all public, already-rendered
  HTML content (no JS execution required, no login, no paywall).
- **robots.txt result**: Requested https://books.toscrape.com/robots.txt once
  — response was 404. No robots file found. (A missing file is not permission
  by itself — it's just a missing file — but combined with the site's own
  stated purpose as a scraping sandbox, this target is appropriate to scrape.)

I will not reuse this code on another site without checking its rules and terms first.

## How to run

```bash
git clone https://github.com/zia0001/fastapi-task-api.git
cd fastapi-task-api/scraper
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
python3 src/main.py
```

Output appears in `output/books.json`, `output/errors.json`, and `output/run-report.json`.

## Lane

Python 3.10+, using `requests` for HTTP, `BeautifulSoup` for HTML parsing, and `Pydantic` for schema validation.

## Record schema

Each validated record in `books.json` has:

| Field | Type | Notes |
|---|---|---|
| `title` | string | Book title |
| `product_url` | URL | Canonical identity of the record |
| `price_gbp` | float | Cleaned numeric price |
| `price_text` | string | Original raw price text, e.g. `"£51.77"` |
| `availability_text` | string | e.g. `"In stock (22 available)"` |
| `rating_text` | string | One / Two / Three / Four / Five |
| `description` | string or null | Some books have none |
| `source_page` | string | Which catalogue page linked to this book |
| `fetched_at` | string (ISO timestamp) | When this record was collected |

## Politeness rules followed

- Identifying `User-Agent` header on every request, naming this project and linking to the repo
- 10-second timeout on every request
- At least 500ms delay between real (non-cached) requests
- Every response's status code checked before parsing
- All pages cached locally after first fetch — re-runs read from disk, never re-hit the site
- Retries once on timeout or `5xx` server errors; never retries `404` or `403`

## Run report (real output, with the deliberate failure test enabled)

```json
{
  "start_time": "2026-09-05T11:09:44.621205+00:00",
  "duration_seconds": 1.940626,
  "pages_fetched": 3,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "failed_page_details": [
    {
      "url": "https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html",
      "reason": "Fetch failed: https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html returned 404 (not retrying)"
    }
  ]
}
```

`TEST_FAILURE_MODE = True` in `main.py` injects one fake, nonexistent book URL on every run to prove one broken page cannot take the whole run down. Set it to `False` for a normal, clean run against only real books.

## Why no browser was needed

All the data used here (title, price, availability, rating, description) is already present in the server-rendered HTML — nothing is loaded via JavaScript after the page loads. A browser (like Playwright) would add significant time and memory cost for zero additional data.

## Ethics note

This scraper only targets a site explicitly built and offered for scraping practice. In general: prefer an official API when one exists, never bypass logins, paywalls, or explicit blocks (like a disallow rule in `robots.txt`), and only collect the data actually needed for the task — nothing more.

## Known limitation

`source_page` currently records the first catalogue page URL for every book, rather than the specific page (1, 2, or 3) that actually linked to it. This doesn't affect record validity or uniqueness, but the provenance field is not fully precise.