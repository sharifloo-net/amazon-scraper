import logging
from pathlib import Path
from typing import List, Dict, Any

# Import configuration
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import REPORTS_DIR, LOG_LEVEL, LOG_FILE

# Set up logging
logging.basicConfig(
	level=getattr(logging, LOG_LEVEL, logging.INFO),
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	filename=LOG_FILE if LOG_FILE else None
)
logger = logging.getLogger(__name__)

# Local imports after config setup
from runners.run_once import run_once
from scraper.database import Database
from reports.exporter import export_prices_to_csv


def run_daily():
	"""Run the daily scraping and reporting workflow."""
	try:
		logger.info("Starting daily scraping and reporting")
		
		# Run the scraper
		run_once()
		
		# Export data to CSV
		db = Database()
		rows = db.get_all_prices()
		
		if not rows:
			logger.warning("No price data found to export")
			return
		
		export_rows = []
		for row in rows:
			export_rows.append((
				row['id'],
				row['title'] or '',
				row['url'],
				row['last_price'] or 0.0,
				row['last_checked'] or '',
			))
		
		# Ensure reports directory exists
		reports_dir = Path(REPORTS_DIR)
		if not reports_dir.is_absolute():
			reports_dir = Path(__file__).resolve().parent.parent / reports_dir
		reports_dir.mkdir(parents=True, exist_ok=True)
		
		# Export to CSV
		filename = export_prices_to_csv(rows, str(reports_dir))
		logger.info(f"Exported price data to: {filename}")
	
	except Exception as e:
		logger.critical(f"Error in daily run: {str(e)}", exc_info=True)
		raise
	finally:
		logger.info("Daily run completed")


if __name__ == '__main__':
	run_daily()
