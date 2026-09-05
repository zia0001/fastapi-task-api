# The Polite Scraper — Books to Scrape

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

I will not reuse this code on another site without checking its rules and
terms first.