import pytest

from scraper.database import Database


def test_ensure_product():
	db = Database('sqlite:///:memory:')
	url = 'https://example.com/p1'
	pid1 = db.ensure_product(url, 'Title A', 10.5)
	assert isinstance(pid1, int)

	rows = db.get_all_prices()
	assert len(rows) == 1
	row = rows[0]
	assert row['id'] == pid1
	assert row['title'] == 'Title A'
	assert row['url'] == url
	assert row['last_price'] == 10.5
	assert row['last_checked']

	pid2 = db.ensure_product(url, 'Title B', 12.34)
	assert pid2 == pid1
	row2 = db.get_all_prices()[0]
	assert row2['title'] == 'Title B'
	assert row2['last_price'] == 12.34
	assert row2['last_checked']


def test_add_price_history_counts():
	db = Database('sqlite:///:memory:')
	url = 'https://example.com/p2'
	pid = db.ensure_product(url, 'Title C', 20.0)

	cur = db.conn.cursor()
	cur.execute("SELECT COUNT(*) FROM price_history WHERE product_id=?", (pid,))
	assert cur.fetchone()[0] == 0

	db.add_price_history(pid, 20.0)
	cur.execute("SELECT COUNT(*) FROM price_history WHERE product_id=?", (pid,))
	assert cur.fetchone()[0] == 1

	db.add_price_history(pid, 19.5)
	cur.execute("SELECT COUNT(*) FROM price_history WHERE product_id=?", (pid,))
	assert cur.fetchone()[0] == 2
