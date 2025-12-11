import pytest

from scraper.parser import clean_price


@pytest.mark.parametrize(
	"raw,expected",
	[
		(None, None),
		("", None),
		("$1,234.56", 1234.56),
		("€1.234,56", 1234.56),
		("59,99", 59.99),
		("59.99", 59.99),
		("1,234", 1234.0),
		("1.234", 1234.0),
		("1.234.567,89", 1234567.89),
		("1,234,567.89", 1234567.89),
		("N/A", None),
	]
)
def test_clean_price_formats(raw, expected):
	assert clean_price(raw) == expected
