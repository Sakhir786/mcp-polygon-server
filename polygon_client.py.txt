import requests
from config import POLYGON_API_KEY, BASE_URL

def get_symbol_lookup(query):
    url = f"{BASE_URL}/v3/reference/tickers?search={query}&apiKey={POLYGON_API_KEY}"
    return requests.get(url).json()

def get_candles(symbol, tf="1day", limit=90):
    multiplier = 1
    url = f"{BASE_URL}/v2/aggs/ticker/{symbol}/range/{multiplier}/{tf}/{limit}/latest?apiKey={POLYGON_API_KEY}"
    return requests.get(url).json()

def get_options_chain(symbol, option_type="call", days_out=30):
    url = f"{BASE_URL}/v3/snapshot/options/{symbol}?apiKey={POLYGON_API_KEY}"
    res = requests.get(url).json()
    contracts = res.get(f"{option_type}s", [])
    filtered = [c for c in contracts if c.get("days_to_expiration", 0) <= days_out]
    return filtered

def get_news(symbol, limit=10):
    url = f"{BASE_URL}/v2/reference/news?ticker={symbol}&limit={limit}&apiKey={POLYGON_API_KEY}"
    return requests.get(url).json()
