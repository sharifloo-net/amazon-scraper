# Amazon Price Tracker (Portfolio-Ready)

Status: CI via GitHub Actions, pytest tests, cron/systemd ready (informational only).

A small, production‑lean scraper that tracks Amazon product prices, stores price history, and exports daily CSV reports. Ready for cron/systemd scheduling, proxies, and logging.

## Features
- Requests + BeautifulSoup scraper with retry/backoff and headers
- Robust price parsing (US/EU formats) and category extraction
- SQLite DB with `products` and `price_history`
- Runners: `once` (scrape + CSV export) and `daily` (wrapper around `once`, prints summary)
- CSV exports to `reports/` and file logging to absolute `LOG_FILE`
- Env‑driven config via `.env`; optional single proxy or random proxies
 
## Problem → Solution
- Problem: Manually tracking product prices and availability is tedious and error‑prone. Pages change, requests get throttled, and insights are lost without a history.
- Solution: A tiny, reliable crawler you can schedule daily. It fetches with retries and jitter, parses title/price/category/availability, saves both “latest” and full history to SQLite, and exports timestamped CSVs.
- Result: One command to run locally or on a server; easy to adapt to new sites; clear logs and tests make it maintainable.

## Table of Contents
- [Problem → Solution](#problem--solution)
- [Project Structure](#project-structure)
- [Quickstart](#quickstart)
- [Setup](#setup)
- [Configuration (.env)](#configuration-env)
- [Run](#run)
- [Example output](#example-output)
- [CLI](#cli)
- [How to adapt to other sites](#how-to-adapt-to-other-sites)
- [Schedule](#schedule)
- [Database schema](#database-schema)
- [Tests](#tests)
- [Screenshots](#screenshots)
- [Troubleshooting](#troubleshooting)
- [Notes](#notes)

## Why this is portfolio‑ready
- Clean structure (fetcher/parser/db separated) and tests.
- Reliable ops: retries, delay jitter, absolute log path, CSV exports.
- Easy deploy: single `.env`, cron/systemd examples, CI included.

## Project Structure
```
amazon_scraper/
├─ main.py                 # CLI entry (once/daily)
├─ config.py               # Loads .env, resolves paths, ensures dirs
├─ products.txt            # One URL per line
├─ runners/
│  ├─ run_once.py          # Scrape all URLs once + export CSV
│  └─ run_daily.py         # Daily wrapper (calls once, prints summary)
├─ scraper/
│  ├─ fetcher.py           # Session, retries, headers, proxy handling
│  ├─ parser.py            # HTML parsing, clean_price
│  └─ database.py          # SQLite schema + price history
├─ reports/
│  └─ exporter.py          # CSV exporter
└─ tests/
   ├─ test_parser.py       # clean_price tests
   ├─ test_fetcher.py      # fetcher session/retry/proxy/delay tests
   └─ test_database.py     # DB insert/update/history tests
```

Additional top-level files (not shown above):
- `requirements.txt`, `README.md`, `.env.example`, `.gitignore`
- `.github/workflows/ci.yml` (CI pipeline)
- `setup.py` (optional packaging/editable install support)
- `logs/` (runtime logs directory; gitignored and created automatically)

## Quickstart
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py once
```

Optional (if you plan to import/package locally):
```
pip install -e .
```

## Setup
1) Python 3.10+ recommended
2) Create a virtualenv and install deps
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Configuration (.env)
Copy `.env.example` to `.env` and adjust as needed.
- `PRODUCTS_FILE` default: `products.txt`
- `REPORTS_DIR` default: `reports`
- `LOG_LEVEL` default: `INFO`
- `LOG_FILE` default: `logs/amazon_scraper.log` (auto‑resolved absolute; dir auto‑created)
- Proxy (choose one):
  - `SCRAPER_PROXY=socks5h://127.0.0.1:9050`
  - or `SCRAPER_USE_RANDOM_PROXIES=true` and define proxies in `scraper/utils.py`

| Variable | Description | Default |
|---|---|---|
| PRODUCTS_FILE | Path to file with one product URL per line | products.txt |
| REPORTS_DIR | Directory for CSV exports | reports |
| LOG_LEVEL | Logging level | INFO |
| LOG_FILE | Log file (resolved to absolute; dir auto‑created) | logs/amazon_scraper.log |
| SCRAPER_PROXY | Single proxy (http/https/socks5h) | — |
| SCRAPER_USE_RANDOM_PROXIES | If true, rotates proxies from `scraper/utils.py` | false |
| REQUEST_TIMEOUT | Seconds per request | 30 |
| REQUEST_RETRIES | HTTP retry count | 5 |
| REQUEST_DELAY | Base delay between requests (jittered) | 1.0 |
| REQUEST_BACKOFF_FACTOR | urllib3 backoff factor | 1.0 |
| AMAZON_DOMAIN | Regional domain | www.amazon.com |
| USER_AGENT | Default user agent | Chromium UA |

## Run
- Scrape once: `python main.py once`
- Daily workflow (scrape + CSV): `python main.py daily`

CSV files are saved to `reports/` with timestamps (both `once` and `daily`). Logs are written to `LOG_FILE` absolute path.

## Example output

CSV (prices_YYYY-MM-DD_HH-MM-SS.csv):
```csv
id,title,url,current_price,last_checked
1,"Apple AirPods Pro","https://www.amazon.com/dp/B0XXXXXX",199.99,2025-12-04T11:47:01+00:00
2,"Logitech MX Master 3S","https://www.amazon.com/dp/B0YYYYYY",89.99,2025-12-04T11:47:01+00:00
```

Terminal/log excerpt:
```text
2025-12-04 11:47:00,812 - scraper.database - INFO - Connected to database: sqlite:///.../data.db
2025-12-04 11:47:01,013 - scraper.fetcher  - INFO - Fetching URL: https://www.amazon.com/dp/B0XXXXXX
2025-12-04 11:47:02,221 - runners.run_once  - INFO - Processing product: https://www.amazon.com/dp/B0XXXXXX
2025-12-04 11:47:02,321 - runners.run_once  - INFO - Updated product: Apple AirPods Pro - $199.99
2025-12-04 11:47:02,522 - reports.exporter  - INFO - Successfully exported 2 rows to reports/prices_2025-12-04_11-47-01.csv
```

CLI output (once):
```text
==> Running once
==> Starting once run
Products file: /path/to/amazon_scraper/products.txt
Loaded 3 URLs
Preparing to export 3 rows to CSV...
Exported 3 rows to: /path/to/amazon_scraper/reports/prices_2025-12-04_11-47-01.csv
==> Once run completed
```

CLI output (daily):
```text
==> Running daily workflow
Exported 3 rows to: /path/to/amazon_scraper/reports/prices_2025-12-04_11-47-01.csv
==> Daily run completed
```

SQLite snapshot (products):
```text
id | title                 | url                                   | last_price | last_checked
---+-----------------------+---------------------------------------+------------+-------------------------------
1  | Apple AirPods Pro     | https://www.amazon.com/dp/B0XXXXXX     | 199.99     | 2025-12-04T11:47:01+00:00
2  | Logitech MX Master 3S | https://www.amazon.com/dp/B0YYYYYY     |  89.99     | 2025-12-04T11:47:01+00:00
```

## CLI
```
python main.py -h
python main.py once
python main.py daily
```

## How to adapt to other sites
- Update selectors in `scraper/parser.py` (e.g., `parse_*` function to extract title/price/category/availability for the new site).
- Tweak headers/host in `scraper/fetcher.py` (or pass site‑specific headers) and set domain/user‑agent in `.env`.
- Reuse `clean_price` or extend it for the site’s number format.
- Keep the `Database` as is, or add columns if the new site has extra fields.
- Optional: create a new runner (e.g., `runners/run_siteX.py`) that reads a different URL list.
- Always respect robots.txt/ToS and add delay/jitter appropriately.

## Schedule
- Cron (9 AM daily; adjust paths):
```
0 9 * * * /home/abolfazl/Documents/python/amazon_scraper/.venv/bin/python \
  /home/abolfazl/Documents/python/amazon_scraper/main.py daily \
  >> /home/abolfazl/Documents/python/amazon_scraper/logs/cron.log 2>&1
```
- systemd (alternative): create a oneshot service + timer pointing to `main.py daily`.

## Database schema
- `products(id, title, url UNIQUE, last_price, last_checked)`
- `price_history(id, product_id → products.id, price, checked_at)`

Common queries are wrapped in `scraper/database.py` (e.g., `get_all_prices()`, `get_price_history()`).

## Tests
Run all tests:
```
pytest -q
```
Covers `clean_price` formats, fetcher session/retry/proxy/delay behaviors, and DB insert/update/history paths.

## Screenshots
Recommended for portfolio: add 1–2 images (terminal run and CSV preview). Save them under `docs/screenshots/` as `terminal-run-once.png` and `exported-csv.png`.
![Terminal: run once](docs/screenshots/terminal-run-once.png)

[//]: # (![CSV preview]&#40;docs/screenshots/exported-csv.png&#41;)

## How I would customize this for a client
- Onboarding: confirm target pages, fields, and regions; gather a few real URLs per template.
- Parsing: add site‑specific parser functions and tests; extend `clean_price` if needed.
- Data model: move to PostgreSQL if larger scale; add indices, unique constraints, and archiving.
- Ops: containerize, add systemd timers or a scheduler (Airflow/Celery), and secrets management.
- Alerts & outputs: email/Slack alerts on price drops; export to Google Sheets/BI dashboards.
- Compliance: rate‑limit, proxy rotation, IP allowlists, and honor site terms.

## Troubleshooting
- Arch/PEP 668 “externally-managed-environment”: create a venv first
  - `python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`
- Cron path issues: always use absolute paths for Python and project.
- No logs: ensure `.env` sets `LOG_FILE`; the directory is auto‑created.
- No CSV: confirm `REPORTS_DIR` is writable and product URLs are valid.

## Notes
- Use region‑appropriate `AMAZON_DOMAIN` in `.env`.
- Respect robots/ToS and rate limits (`REQUEST_DELAY`, retries).
- For dynamic pages, add Selenium only when necessary.