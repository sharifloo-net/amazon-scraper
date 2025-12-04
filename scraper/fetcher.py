import time
from typing import Dict, Any, Optional
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Import configuration
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import (
	SCRAPER_PROXY, SCRAPER_USE_RANDOM_PROXIES, REQUEST_TIMEOUT,
	REQUEST_DELAY, REQUEST_RETRIES, REQUEST_BACKOFF_FACTOR,
	AMAZON_DOMAIN, USER_AGENT, LOG_LEVEL, LOG_FILE
)
from .utils import get_random_proxy

# Set up logging
import logging

logging.basicConfig(
	level=getattr(logging, LOG_LEVEL, logging.INFO),
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	filename=LOG_FILE if LOG_FILE else None
)
logger = logging.getLogger(__name__)


def create_session() -> Session:
	"""Create a configured requests Session with retry strategy."""
	session = Session()
	
	retry_strategy = Retry(
		total=REQUEST_RETRIES,
		backoff_factor=REQUEST_BACKOFF_FACTOR,
		status_forcelist=[429, 500, 502, 503, 504],
		allowed_methods=["GET"]
	)
	
	adapter = HTTPAdapter(
		max_retries=retry_strategy,
		pool_connections=10,
		pool_maxsize=10
	)
	
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	
	logger.debug("Created new session with retry strategy")
	return session


def get_page(url: str) -> str:
	"""
	Fetch a web page with configurable settings.
	
	Args:
		url: The URL to fetch
		
	Returns:
		str: The response text
		
	Raises:
		requests.exceptions.RequestException: If the request fails
	"""
	session = create_session()
	
	try:
		# Proxy configuration
		proxy = SCRAPER_PROXY if SCRAPER_PROXY else (get_random_proxy() if SCRAPER_USE_RANDOM_PROXIES else None)
		proxies = {'http': proxy, 'https': proxy} if proxy else None
		
		# Headers
		headers = {
			"User-Agent": USER_AGENT,
			"Accept-Language": "en-US,en;q=0.5",
			'Host': AMAZON_DOMAIN,
			'Origin': f'https://{AMAZON_DOMAIN}',
			'Connection': 'keep-alive',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate, br',
			'DNT': '1',
			'Referer': f'https://{AMAZON_DOMAIN}/',
			'Upgrade-Insecure-Requests': '1'
		}
		
		# Add delay between requests to be nice to Amazon
		if REQUEST_DELAY > 0:
			logger.debug(f"Waiting {REQUEST_DELAY} seconds before request")
			time.sleep(REQUEST_DELAY)
		
		logger.info(f"Fetching URL: {url}")
		if proxies:
			logger.debug(f"Using proxy: {proxies}")
		
		response = session.get(
			url,
			headers=headers,
			proxies=proxies,
			timeout=REQUEST_TIMEOUT,
			allow_redirects=True
		)
		response.raise_for_status()
		
		logger.debug(f"Successfully fetched {url} (Status: {response.status_code})")
		return response.text
	
	except Exception as e:
		logger.error(f"Error fetching {url}: {str(e)}")
		raise
	finally:
		session.close()
