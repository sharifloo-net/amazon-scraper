# Amazon Price Tracker (Portfolio-Ready)

Status: CI via GitHub Actions, pytest tests, cron/systemd ready (informational only).

A small, production‑lean scraper that tracks Amazon product prices, stores price history, and exports daily CSV reports. Ready for cron/systemd scheduling, proxies, and logging.

## Features
- Requests + BeautifulSoup scraper with retry/backoff and headers
- Robust price parsing (US/EU formats) and category extraction
- SQLite DB with `products` and `price_history`
- Runners: `once` (scrape) and `daily` (scrape + CSV export)
- CSV exports to `reports/` and file logging to absolute `LOG_FILE`
- Env‑driven config via `.env`; optional single proxy or random proxies

## Table of Contents
- [Project Structure](#project-structure)
- [Quickstart](#quickstart)
- [Setup](#setup)
- [Configuration (.env)](#configuration-env)
- [Run](#run)
- [CLI](#cli)
- [Schedule](#schedule)
- [Database schema](#database-schema)
- [Tests](#tests)
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
│  ├─ run_once.py          # Scrape all URLs once
│  └─ run_daily.py         # Scrape + export CSV
├─ scraper/
│  ├─ fetcher.py           # Session, retries, headers, proxy handling
│  ├─ parser.py            # HTML parsing, _clean_price
│  └─ database.py          # SQLite schema + price history
├─ reports/
│  └─ exporter.py          # CSV exporter
└─ tests/
   ├─ test_parser.py       # _clean_price tests
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

CSV files are saved to `reports/` with timestamps. Logs are written to `LOG_FILE` absolute path.

## CLI
```
python main.py -h
python main.py once
python main.py daily
```

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
Covers `_clean_price` formats and DB insert/update/history paths.

## Screenshots (recommended for portfolio)
- Add 1–2 CSV previews from `reports/` and a snippet of the log file.
- Optionally include a small chart of price history.

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