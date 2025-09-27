import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

def get_symbol_lookup(query):
    url = f"{BASE_URL}/v3/reference/tickers?search={query}&active=true&apiKey={API_KEY}"
    return requests.get(url).json()

def get_candles(symbol, tf="day", limit=90):
    url = f"{BASE_URL}/v2/aggs/ticker/{symbol}/range/1/{tf}/2023-01-01/2025-12-31?limit={limit}&apiKey={API_KEY}"
    return requests.get(url).json()

def get_options_chain(symbol, option_type="call", days_out=30):
    url = f"{BASE_URL}/v3/snapshot/options/{symbol}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_news(symbol):
    url = f"{BASE_URL}/v2/reference/news?ticker={symbol}&limit=5&apiKey={API_KEY}"
    return requests.get(url).json()

def get_quote(symbol):
    url = f"{BASE_URL}/v2/last/nbbo/{symbol}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_last_trade(symbol):
    url = f"{BASE_URL}/v2/last/trade/{symbol}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_ticker_details(symbol):
    url = f"{BASE_URL}/v3/reference/tickers/{symbol}?apiKey={API_KEY}"
    return requests.get(url).json()
