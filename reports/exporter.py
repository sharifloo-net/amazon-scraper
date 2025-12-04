import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Optional, Tuple

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


def export_prices_to_csv(
		rows: List[Tuple[Any, ...]],
		output_dir: Optional[Union[str, Path]] = None
) -> str:
	"""Export price data to a CSV file.
	
	Args:
		rows: List of price data rows to export
		output_dir: Directory to save the CSV file. If None, uses REPORTS_DIR from config.
				   Can be relative or absolute path.
				   
	Returns:
		str: Path to the generated CSV file
		
	Raises:
		ValueError: If no rows are provided
		OSError: If there's an error writing the file
	"""
	if not rows:
		logger.warning("No data rows provided for export")
		raise ValueError("No data rows provided for export")
	
	# Determine output directory
	output_dir = Path(output_dir or REPORTS_DIR)
	
	# Resolve relative paths relative to project root if needed
	if not output_dir.is_absolute():
		output_dir = Path(__file__).resolve().parent.parent / output_dir
	
	# Ensure the directory exists
	output_dir.mkdir(parents=True, exist_ok=True)
	
	# Generate filename with timestamp
	timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	filename = output_dir / f'prices_{timestamp}.csv'
	
	try:
		with open(filename, 'w', newline='', encoding='utf-8') as f:
			writer = csv.writer(f)
			
			# Write header
			writer.writerow([
				'id',
				'title',
				'url',
				'current_price',
				# 'price_change',
				'last_checked',
				# 'created_at',
				# 'updated_at'
			])
			
			# Write data rows
			for row in rows:
				writer.writerow(row)
		
		logger.info(f"Successfully exported {len(rows)} rows to {filename}")
		return str(filename)
	
	except Exception as e:
		logger.error(f"Error exporting to CSV: {str(e)}")
		raise
