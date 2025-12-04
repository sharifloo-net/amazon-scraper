"""Configuration settings loaded from environment variables."""
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

import os
from typing import Optional

# Database
DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///data.db')

# Input/Output
PRODUCTS_FILE: str = os.getenv('PRODUCTS_FILE', 'products.txt')
REPORTS_DIR: str = os.getenv('REPORTS_DIR', 'reports')

# Proxies
SCRAPER_PROXY: Optional[str] = os.getenv('SCRAPER_PROXY')
SCRAPER_USE_RANDOM_PROXIES: bool = os.getenv('SCRAPER_USE_RANDOM_PROXIES', 'false').lower() == 'true'

# Request settings
REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
REQUEST_RETRIES: int = int(os.getenv('REQUEST_RETRIES', '5'))
REQUEST_DELAY: float = float(os.getenv('REQUEST_DELAY', '1.0'))
REQUEST_BACKOFF_FACTOR: float = float(os.getenv('REQUEST_BACKOFF_FACTOR', '1.0'))

# Amazon-specific
AMAZON_DOMAIN: str = os.getenv('AMAZON_DOMAIN', 'www.amazon.com')
USER_AGENT: str = os.getenv('USER_AGENT',
                            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# Logging
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FILE: str = os.getenv('LOG_FILE', 'logs/amazon_scraper.log')

# Ensure directories exist
Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)
if LOG_FILE:
	Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
