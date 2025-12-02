from scraper.client import HttpClient
from scraper.parser import parse_amazon_product


def main():
	url = "https://www.amazon.com/KIDMI-Leather-Footbed-Sandals-Support/dp/B0BS6G9WG6?ref=dlx_cyber_dg_dcl_B0BS6G9WG6_dt_sl7_ea_pi&pf_rd_r=GS9DQXSHB2QATQHWR6WA&pf_rd_p=c7b65c9c-6925-4963-97bf-41ed14595eea&th=1&psc=1"
	client = HttpClient()
	html = client.get(url)
	data = parse_amazon_product(html)
	print('Parsed result:')
	for k, v in data.items():
		print(f'{k.capitalize().replace('_', ' ')}: {str(v).replace('›', ' › ')}')


if __name__ == '__main__':
	main()
