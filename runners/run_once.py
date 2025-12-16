from pathlib import Path
import logging
from typing import List

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import PRODUCTS_FILE, LOG_LEVEL, LOG_FILE, REPORTS_DIR
from scraper.fetcher import get_page
from scraper.parser import parse_amazon_product
from scraper.database import Database
from reports.exporter import export_prices_to_csv

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE if LOG_FILE else None
)
logger = logging.getLogger(__name__)


def load_product_urls(products_file: str) -> List[str]:
    """Load product URLs from a file.
    
    Args:
        products_file: Path to the file containing product URLs
        
    Returns:
        List of product URLs
    """
    try:
        with open(products_file) as f:
            urls = [u.strip() for u in f if u.strip()]
        logger.info(f"Loaded {len(urls)} product URLs from {products_file}")
        return urls
    except FileNotFoundError:
        logger.error(f"Products file not found: {products_file}")
        raise
    except Exception as e:
        logger.error(f"Error loading product URLs: {str(e)}")
        raise


def process_product(url: str, db: Database) -> None:
    """Process a single product URL.
    
    Args:
        url: Product URL to process
        db: Database instance
    """
    try:
        logger.info(f"Processing product: {url}")
        html = get_page(url)
        data = parse_amazon_product(html)
        
        title = data.get('title')
        price = data.get('price')
        
        if not title or price is None:
            logger.warning(f"Missing data for {url}: title={title is not None}, price={price is not None}")
            return
            
        product_id = db.ensure_product(url, title, price)
        db.add_price_history(product_id, price)
        logger.info(f"Updated product: {title} - ${price:.2f}")
        
    except Exception as e:
        logger.error(f"Error processing {url}: {str(e)}")
        raise


def run_once(verbose: bool = True):
    """Run the scraper once for all products."""
    try:
        # Resolve products file path
        products_file = Path(PRODUCTS_FILE)
        if not products_file.is_absolute():
            root = Path(__file__).resolve().parent.parent
            products_file = root / products_file
        
        if verbose:
            print("==> Starting once run")
            print(f"Products file: {products_file}")
        logger.info("Starting product scraper")
        urls = load_product_urls(str(products_file))
        
        if verbose:
            print(f"Loaded {len(urls)} URLs")
        if not urls:
            logger.warning("No product URLs found to process")
            if verbose:
                print("No product URLs found to process.")
            return {"urls": 0, "exported_rows": 0, "csv_path": None}
            
        db = Database()
        
        for url in urls:
            process_product(url, db)
            
        # Prepare CSV export of current prices
        rows = db.get_all_prices()
        if not rows:
            logger.warning("No price data found to export")
            if verbose:
                print("No price data found to export.")
            logger.info("Product scraping completed successfully")
            if verbose:
                print("==> Once run completed")
            return {"urls": len(urls), "exported_rows": 0, "csv_path": None}

        if verbose:
            print(f"Preparing to export {len(rows)} rows to CSV...")

        # Build export rows
        export_rows = []
        for row in rows:
            export_rows.append((
                row['id'],
                row['title'] or '',
                row['url'],
                row['last_price'] or 0.0,
                row['last_checked'] or '',
            ))

        # Resolve and ensure reports directory
        reports_dir = Path(REPORTS_DIR)
        if not reports_dir.is_absolute():
            reports_dir = Path(__file__).resolve().parent.parent / reports_dir
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Export to CSV
        filename = export_prices_to_csv(export_rows, str(reports_dir))
        logger.info(f"Exported price data to: {filename}")
        if verbose:
            print(f"Exported {len(export_rows)} rows to: {filename}")

        logger.info("Product scraping completed successfully")
        if verbose:
            print("==> Once run completed")
        return {"urls": len(urls), "exported_rows": len(export_rows), "csv_path": filename}
        
    except Exception as e:
        logger.critical(f"Fatal error in run_once: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    run_once()
