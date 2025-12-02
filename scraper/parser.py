from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, Any


def _clean_price(text: Optional[str]) -> Optional[float]:
	if not text:
		return None
	s = re.sub(r'[^\d.,]', '', text)
	if not s:
		return None
	
	# if ',' in s and s.count(',') == 1 and '.' not in s:
	# 	s = s.replace(',', '.')
	
	s = s.replace(',', '') if '.' in s else s
	try:
		return float(s)
	except ValueError as e:
		print(e)
		return None


def parse_amazon_product(html: str) -> Dict[str, Any]:
	soup = BeautifulSoup(html, 'lxml')
	
	title_el = soup.select_one('#productTitle')
	title = title_el.get_text(strip=True) if title_el else None
	
	price_el = soup.select_one('#corePrice_feature_div > div > div > span.a-price > span.a-offscreen')
	price_text = price_el.get_text(strip=True) if price_el else None
	price_text = price_text.replace('GBP', '£')
	price = _clean_price(price_text)
	
	category_el = soup.select_one("#wayfinding-breadcrumbs_feature_div > ul")
	category = category_el.get_text(strip=True) if category_el else None
	
	availability_el = soup.select_one("#availability > span")
	availability = availability_el.get_text(strip=True) if availability_el else None
	
	return {
		'title': title,
		'price': f'{price: ,.2f}',
		'price_text': price_text,
		'category': category,
		'availability': availability
	}
