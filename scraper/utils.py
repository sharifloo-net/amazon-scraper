import random

PROXIES = [
	None, # 1 call with no proxy
	'http://test.com:8000',
	'http://example.com:8080',
	'http://foo.com:3128'
]

def get_random_proxy():
	return random.choice(PROXIES)