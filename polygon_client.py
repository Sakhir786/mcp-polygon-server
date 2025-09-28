import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

# ---------------- Existing functions ----------------

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

def get_fundamentals(symbol):
    # Use Polygon's financials endpoint
    url = f"{BASE_URL}/vX/reference/financials?ticker={symbol.upper()}&limit=1&apiKey={API_KEY}"
    return requests.get(url).json()

# ---------------- New functions (snapshots + aggs) ----------------

def get_daily_market_summary(date):
    """Daily market summary for US stocks"""
    url = f"{BASE_URL}/v2/aggs/grouped/locale/us/market/stocks/{date}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_previous_day_bar(ticker):
    """Previous day OHLCV for a ticker"""
    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/prev?apiKey={API_KEY}"
    return requests.get(url).json()

def get_single_stock_snapshot(ticker):
    """Snapshot for a single stock ticker"""
    url = f"{BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_full_market_snapshot():
    """Snapshot for entire US stock market"""
    url = f"{BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={API_KEY}"
    return requests.get(url).json()

def get_unified_snapshot():
    """Unified snapshot for stocks, options, and crypto"""
    url = f"{BASE_URL}/v2/snapshot?apiKey={API_KEY}"
    return requests.get(url).json()

def get_all_option_contracts():
    """List all option contracts"""
    url = f"{BASE_URL}/v3/reference/options/contracts?apiKey={API_KEY}"
    return requests.get(url).json()

def get_option_aggregates(options_ticker, multiplier, timespan, from_date, to_date):
    """Aggregate bars for an option contract"""
    url = f"{BASE_URL}/v2/aggs/ticker/{options_ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_option_previous_day_bar(options_ticker):
    """Previous day OHLCV for an option contract"""
    url = f"{BASE_URL}/v2/aggs/ticker/{options_ticker}/prev?apiKey={API_KEY}"
    return requests.get(url).json()

def get_option_contract_snapshot(options_ticker):
    """Snapshot for a single option contract"""
    url = f"{BASE_URL}/v2/snapshot/locale/us/markets/options/tickers/{options_ticker}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_option_chain_snapshot(underlying_asset):
    """Snapshot of full option chain for underlying asset"""
    url = f"{BASE_URL}/v3/snapshot/options/{underlying_asset}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_unified_option_snapshot():
    """Unified option snapshot (all contracts)"""
    url = f"{BASE_URL}/v3/snapshot/options?apiKey={API_KEY}"
    return requests.get(url).json()
