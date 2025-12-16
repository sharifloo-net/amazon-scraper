import logging

# Import configuration
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import LOG_LEVEL, LOG_FILE

# Set up logging
logging.basicConfig(
	level=getattr(logging, LOG_LEVEL, logging.INFO),
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	filename=LOG_FILE if LOG_FILE else None
)
logger = logging.getLogger(__name__)

# Local imports after config setup
from runners.run_once import run_once


def run_daily():
	"""Run the daily scraping and reporting workflow."""
	try:
		logger.info("Starting daily scraping and reporting")
		
		# Run the scraper + export via run_once
		summary = run_once(verbose=False)
		urls = summary.get("urls", 0) if isinstance(summary, dict) else 0
		exported = summary.get("exported_rows", 0) if isinstance(summary, dict) else 0
		csv_path = summary.get("csv_path") if isinstance(summary, dict) else None
		
		if exported:
			print(f"Exported {exported} rows to: {csv_path}")
		else:
			logger.warning("No price data found to export")
			print("No price data found to export.")
		
		return summary
	
	except Exception as e:
		logger.critical(f"Error in daily run: {str(e)}", exc_info=True)
		raise
	finally:
		logger.info("Daily run completed")
		print("==> Daily run completed")


if __name__ == '__main__':
	run_daily()
