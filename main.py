import argparse
from runners.run_once import run_once
from runners.run_daily import run_daily


def main():
	parser = argparse.ArgumentParser(description='Amazon scraper runner')
	sub = parser.add_subparsers(dest='command')
	sub.required = False
	sub.add_parser('once', help='Run scraping once')
	sub.add_parser('daily', help='Run scrape then export CSV')
	args = parser.parse_args()
	cmd = args.command or 'once'
	
	if cmd == 'daily':
		run_daily()
	else:
		run_once()


if __name__ == '__main__':
	main()
