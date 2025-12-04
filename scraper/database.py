import sqlite3
import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# Import configuration
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import DATABASE_URL, LOG_LEVEL, LOG_FILE

# Set up logging
import logging

logging.basicConfig(
	level=getattr(logging, LOG_LEVEL, logging.INFO),
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	filename=LOG_FILE if LOG_FILE else None
)
logger = logging.getLogger(__name__)


class Database:
	def __init__(self, db_url: Optional[str] = None):
		"""Initialize database connection using DATABASE_URL from config.
		
		Args:
			db_url: Optional database URL. If not provided, uses DATABASE_URL from config.
				   Format: sqlite:///path/to/db or postgresql://user:pass@host:port/dbname
		"""
		self.db_url = db_url or DATABASE_URL
		self.conn = self._create_connection()
		self.conn.row_factory = sqlite3.Row
		self._create_tables()
		logger.info(f"Connected to database: {self._obfuscate_url(self.db_url)}")
	
	def _create_connection(self):
		"""Create a database connection based on the URL scheme."""
		parsed = urlparse(self.db_url)
		
		if parsed.scheme == 'sqlite':
			# SQLite connection
			db_path = parsed.path.lstrip('/')
			if db_path == ':memory:' or not db_path:
				return sqlite3.connect(':memory:')
			
			# Resolve relative paths relative to project root
			db_file = Path(db_path)
			if not db_file.is_absolute():
				db_file = Path(__file__).resolve().parent.parent / db_path
			
			# Ensure directory exists
			db_file.parent.mkdir(parents=True, exist_ok=True)
			
			return sqlite3.connect(str(db_file))
		
		elif parsed.scheme.startswith('postgres'):
			# PostgreSQL connection (requires psycopg2)
			try:
				import psycopg2
				from psycopg2.extras import DictCursor
				
				# Extract connection parameters
				dbname = parsed.path[1:]  # Remove leading /
				user = parsed.username
				password = parsed.password
				host = parsed.hostname
				port = parsed.port or 5432
				
				return psycopg2.connect(
					dbname=dbname,
					user=user,
					password=password,
					host=host,
					port=port,
					cursor_factory=DictCursor
				)
			except ImportError:
				raise ImportError(
					"PostgreSQL support requires psycopg2. "
					"Install with: pip install psycopg2-binary"
				)
		else:
			raise ValueError(f"Unsupported database scheme: {parsed.scheme}")
	
	def _obfuscate_url(self, url: str) -> str:
		"""Obfuscate sensitive information in database URLs for logging."""
		parsed = urlparse(url)
		if parsed.password:
			# Replace password with *** for logging
			netloc = f"{parsed.username}:***@{parsed.hostname}"
			if parsed.port:
				netloc += f":{parsed.port}"
			return parsed._replace(netloc=netloc).geturl()
		return url
		
	def _create_tables(self):
		cur = self.conn.cursor()
		
		cur.execute("""
                    CREATE TABLE IF NOT EXISTS products
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        title
                        TEXT,
                        url
                        TEXT
                        UNIQUE,
                        last_price
                        REAL,
                        last_checked
                        TEXT
                    )
		            """)
		
		cur.execute("""
                    CREATE TABLE IF NOT EXISTS price_history
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        product_id
                        INTEGER,
                        price
                        REAL,
                        checked_at
                        TEXT,
                        FOREIGN
                        KEY
                    (
                        product_id
                    )
                        REFERENCES products
                    (
                        id
                    )
                        )
		            """)
		
		self.conn.commit()
	
	def ensure_product(self, url: str, title: str, price: Optional[float]):
		"""Insert product if new. Return product_id."""
		cur = self.conn.cursor()
		cur.execute('SELECT id FROM products WHERE url = ?', (url,))
		row: sqlite3.Row = cur.fetchone()
		
		now = datetime.now(timezone.utc).isoformat()
		
		if row:
			product_id = row['id']
			cur.execute(
				"UPDATE products SET title = ?, last_price = ?, last_checked = ? WHERE id = ?",
				(title, price, now, product_id)
			)
		else:
			cur.execute(
				"INSERT INTO products (title, url, last_price, last_checked) VALUES (?, ?, ?, ?)",
				(title, url, price, now)
			)
			product_id = cur.lastrowid
		
		self.conn.commit()
		return product_id
	
	def add_price_history(self, product_id: int, price: Optional[float]):
		cur = self.conn.cursor()
		cur.execute(
			"INSERT INTO price_history (product_id, price, checked_at) VALUES (?, ?, ?)",
			(product_id, price, datetime.now(timezone.utc).isoformat())
		)
		self.conn.commit()
	
	def get_all_prices(self):
		cur = self.conn.cursor()
		cur.execute(
			"SELECT * FROM products"
		)
		self.conn.commit()
		return cur.fetchall()
