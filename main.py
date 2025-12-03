from scraper.client import HttpClient
from scraper.parser import parse_amazon_product
from scraper.database import Database


def main():
	with open('products.txt', 'r', encoding='utf-8') as f:
		urls = [line.strip() for line in f.readlines() if line.strip()]
	client = HttpClient()
	db = Database()
	
	for url in urls:
		print('Scraping:', url)
		print('Fetching page...')
		html = client.get(url)
		
		print('Parsing...')
		data = parse_amazon_product(html)
		
		# Extract parsed fields
		title = data.get('title')
		price = data.get('price')
		
		# Save/update product
		product_id = db.ensure_product(url, title, price)
		
		# Add price history entry
		db.add_price_history(product_id, price)
		
		# Print parsed output
		print('\nSaved to database.')
		print(f'Product ID: {product_id}')
		print(f'Price: {price:,.2f}' if price else 'Price: Not available!')
		print(f'Category: {data.get('category')}' if data.get('category') else 'Category: Not available!')
		print(f'Availability: {data.get('availability')}' if data.get('availability') else 'Availability: Not available!')
		print()


if __name__ == '__main__':
	main()
