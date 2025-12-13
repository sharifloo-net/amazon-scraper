import pytest
from unittest.mock import patch, MagicMock, call
import requests
from requests.exceptions import RequestException, Timeout, HTTPError

from scraper.fetcher import create_session, get_page


class TestCreateSession:
	def test_create_session_with_retry_strategy(self):
		"""Test that create_session returns a session with proper retry configuration."""
		session = create_session()
		
		# Check session has the right adapters mounted
		assert 'http://' in session.adapters
		assert 'https://' in session.adapters
		
		# Check retry configuration
		adapter = session.adapters['http://']
		assert adapter.max_retries.total == 3  # Default from config
		assert adapter.max_retries.status_forcelist == [429, 500, 502, 503, 504]


class TestGetPage:
	@pytest.fixture(autouse=True)
	def mock_session(self):
		with patch('scraper.fetcher.create_session') as mock_create:
			mock_session = MagicMock()
			mock_response = MagicMock()
			mock_response.text = "<html>Test Content</html>"
			mock_response.status_code = 200
			mock_session.get.return_value = mock_response
			mock_create.return_value = mock_session
			yield mock_session, mock_response
	
	@pytest.fixture(autouse=True)
	def mock_time_sleep(self):
		with patch('time.sleep') as mock_sleep:
			yield mock_sleep
	
	def test_get_page_success(self, mock_session):
		"""Test successful page fetch."""
		mock_session, mock_response = mock_session
		url = "https://www.amazon.com/test"
		
		result = get_page(url)
		
		mock_session.get.assert_called_once()
		assert result == "<html>Test Content</html>"
		mock_session.close.assert_called_once()
	
	def test_get_page_with_proxy(self, mock_session, monkeypatch):
		"""Test page fetch with proxy configuration."""
		mock_session, _ = mock_session
		
		monkeypatch.setattr('scraper.fetcher.SCRAPER_PROXY', None)
		monkeypatch.setattr('scraper.fetcher.SCRAPER_USE_RANDOM_PROXIES', True)
		monkeypatch.setattr('scraper.fetcher.get_random_proxy', lambda: 'http://proxy:1234')
		
		get_page("https://www.amazon.com/test")
		
		# Check if proxy was used in the request
		args, kwargs = mock_session.get.call_args
		assert 'proxies' in kwargs
		assert kwargs['proxies'] == {
			'http': 'http://proxy:1234',
			'https': 'http://proxy:1234'
		}
	
	def test_get_page_with_request_delay(self, mock_session, mock_time_sleep, monkeypatch):
		"""Test that delay is added between requests."""
		mock_session, _ = mock_session
		monkeypatch.setattr('scraper.fetcher.REQUEST_DELAY', 1.0)
		
		get_page("https://www.amazon.com/test")
		
		# Check if sleep was called with a value around 1 second (±0.5)
		mock_time_sleep.assert_called_once()
		sleep_time = mock_time_sleep.call_args[0][0]
		assert 0.5 <= sleep_time <= 1.5
	
	def test_get_page_http_error(self, mock_session):
		"""Test handling of HTTP errors."""
		mock_session, mock_response = mock_session
		mock_response.raise_for_status.side_effect = HTTPError("Test error")
		
		with pytest.raises(RequestException):
			get_page("https://www.amazon.com/error")
		
		mock_session.close.assert_called_once()
	
	def test_get_page_timeout(self, mock_session):
		"""Test handling of request timeout."""
		mock_session, _ = mock_session
		mock_session.get.side_effect = Timeout("Request timed out")
		
		with pytest.raises(RequestException):
			get_page("https://www.amazon.com/timeout")
		
		mock_session.close.assert_called_once()
	
	def test_get_page_general_exception(self, mock_session):
		"""Test handling of general exceptions."""
		mock_session, _ = mock_session
		mock_session.get.side_effect = RequestException("Unexpected error")
		
		with pytest.raises(RequestException):
			get_page("https://www.amazon.com/error")
		
		mock_session.close.assert_called_once()
