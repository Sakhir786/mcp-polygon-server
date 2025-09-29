import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

# ---------------- Core endpoints ----------------

def get_symbol_lookup(query: str):
    url = f"{BASE_URL}/v3/reference/tickers?search={query}&active=true&apiKey={API_KEY}"
    return requests.get(url).json()

def get_candles(symbol: str, tf: str = "day", limit: int = 730):
    url = (
        f"{BASE_URL}/v2/aggs/ticker/{symbol}/range/1/{tf}/2023-01-01/2025-12-31"
        f"?limit={limit}&apiKey={API_KEY}"
    )
    return requests.get(url).json()

def get_options_chain(symbol: str, option_type: str = "call", days_out: int = 30):
    # Snapshot of options chain for a symbol
    url = f"{BASE_URL}/v3/snapshot/options/{symbol}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_news(symbol: str):
    url = f"{BASE_URL}/v2/reference/news?ticker={symbol}&limit=5&apiKey={API_KEY}"
    return requests.get(url).json()

def get_last_trade(symbol: str):
    url = f"{BASE_URL}/v2/last/trade/{symbol}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_ticker_details(symbol: str):
    url = f"{BASE_URL}/v3/reference/tickers/{symbol}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_fundamentals(symbol: str):
    url = f"{BASE_URL}/vX/reference/financials?ticker={symbol.upper()}&limit=1&apiKey={API_KEY}"
    return requests.get(url).json()

def get_previous_day_bar(ticker: str):
    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/prev?apiKey={API_KEY}"
    return requests.get(url).json()

def get_single_stock_snapshot(ticker: str):
    url = f"{BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={API_KEY}"
    return requests.get(url).json()

# ---------------- Options endpoints ----------------

def get_all_option_contracts(underlying_ticker: str, expiration_date: str | None = None, limit: int = 50):
    """List all option contracts for a given underlying, with optional expiry filter."""
    url = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={underlying_ticker}&limit={limit}&apiKey={API_KEY}"
    if expiration_date:
        url += f"&expiration_date.gte={expiration_date}"
    return requests.get(url).json()

def get_option_aggregates(options_ticker: str, multiplier: int, timespan: str, from_date: str, to_date: str):
    url = (
        f"{BASE_URL}/v2/aggs/ticker/{options_ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        f"?apiKey={API_KEY}"
    )
    return requests.get(url).json()

def get_option_previous_day_bar(options_ticker: str):
    url = f"{BASE_URL}/v2/aggs/ticker/{options_ticker}/prev?apiKey={API_KEY}"
    return requests.get(url).json()

def get_option_chain_snapshot(underlying_asset: str, cursor: str | None = None, limit: int = 50):
    """Get paginated option chain snapshot for an underlying."""
    url = f"{BASE_URL}/v3/snapshot/options/{underlying_asset}?limit={limit}&apiKey={API_KEY}"
    if cursor:
        url += f"&cursor={cursor}"
    return requests.get(url).json()

def get_option_contract_snapshot(underlying: str, contract: str):
    """Snapshot for a single option contract (Polygon requires both underlying + contract)."""
    url = f"{BASE_URL}/v3/snapshot/options/{underlying}/{contract}?apiKey={API_KEY}"
    return requests.get(url).json()

