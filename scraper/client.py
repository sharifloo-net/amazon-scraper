import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry



class HttpClient:
	def __init__(self):
		self.session = requests.session()
		self.proxies = {
			'http': 'socks5h://127.0.0.1:12334',
			'https': 'socks5h://127.0.0.1:12334'
		}
		self._configure()
	
	def _configure(self):
		retry_strategy = Retry(
			total=3,
			backoff_factor=0.3,
			status_forcelist=[429, 500, 502, 503, 504],
			allowed_methods=['GET', 'HEAD']
		)
		
		adapter = HTTPAdapter(max_retries=retry_strategy)
		self.session.mount('http://', adapter)
		self.session.mount('https://', adapter)
		
		self.session.headers.update({
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
			              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
			"Accept-Language": "en-US,en;q=0.5",
			'Host': 'www.amazon.com',
			'Origin': 'https://www.amazon.com',
			'Connection': 'keep - alive',
			'Referer': 'https://www.amazon.com'
		})
		
	def get(self, url: str):
		"""Fetch a page and return the HTML text."""
		response = self.session.get(url, timeout=20, proxies=self.proxies)
		response.raise_for_status()
		return response.text
		