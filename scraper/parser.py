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


def _clean_category(breadcrumb: str) -> str:
	items = [item.strip() for item in breadcrumb.split('›') if item.strip()]
	return ' > '.join(items)


def parse_amazon_product(html: str) -> Dict[str, Any]:
	soup = BeautifulSoup(html, 'lxml')
	
	title_el = soup.select_one('#productTitle')
	title = title_el.get_text(strip=True) if title_el else None
	
	price_el = soup.select_one('#corePrice_feature_div > div > div > span.a-price > span.a-offscreen')
	price_text = price_el.get_text(strip=True) if price_el else None
	price = _clean_price(price_text)
	
	category_el = soup.select_one("#wayfinding-breadcrumbs_feature_div > ul")
	if category_el:
		items = [item.strip() for item in category_el.get_text(strip=True).split('›') if item.strip()]
		category = ' > '.join(items)
	else:
		category = None
	
	availability_el = soup.select_one("#availability > span")
	availability = availability_el.get_text(strip=True) if availability_el else None
	
	return {
		'title': title,
		'price': price,
		'category': category,
		'availability': availability
	}
