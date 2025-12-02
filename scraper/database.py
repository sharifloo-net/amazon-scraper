import sqlite3
from typing import Optional, Dict, Any
from datetime import datetime, timezone

class Database:
	def __init__(self, db_path: str = 'data.db'):
		self.conn = sqlite3.connect(db_path)
		self.conn.row_factory = sqlite3.Row
		self._create_tables()
	
	def _create_tables(self):
		cur = self.conn.cursor()
		
		cur.execute("""
		CREATE TABLE IF NOT EXISTS products (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			url TEXT UNIQUE,
			title TEXT,
			last_price REAL,
			last_checked TEXT
		)
		""")
		
		cur.execute("""
		CREATE TABLE IF NOT EXISTS price_history (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			product_id INTEGER,
			price REAL,
			checked_at TEXT,
			FOREIGN KEY(product_id) REFERENCES products(id)
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
				"INSERT INTO products (url, title, last_price, last_checked) VALUES (?, ?, ?, ?)",
				(url, title, price, now)
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