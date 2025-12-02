from scraper.client import HttpClient
from scraper.parser import parse_amazon_product
from scraper.database import Database


def main():
	# url = "https://www.amazon.com/KIDMI-Leather-Footbed-Sandals-Support/dp/B0BS6G9WG6?ref=dlx_cyber_dg_dcl_B0BS6G9WG6_dt_sl7_ea_pi&pf_rd_r=GS9DQXSHB2QATQHWR6WA&pf_rd_p=c7b65c9c-6925-4963-97bf-41ed14595eea&th=1&psc=1"
	url = 'https://www.amazon.com/SAMSUNG-Essential-Computer-Advanced-LS27D366GANXZA/dp/B0DB9Q5G3R?currency=USD'
	
	client = HttpClient()
	db = Database()
	
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
	print(f'Price: {price}')
	print(f'Category: {data.get('category')}')
	print(f'Availability: {data.get('availability')}')


if __name__ == '__main__':
	main()
