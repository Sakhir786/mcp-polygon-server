import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

# ---------------- Core endpoints ----------------

def get_symbol_lookup(query: str):
    """Search tickers by keyword"""
    url = f"{BASE_URL}/v3/reference/tickers?search={query}&active=true&apiKey={API_KEY}"
    return requests.get(url).json()

def get_candles(symbol: str, tf: str = "day", limit: int = 90):
    """Historical OHLCV candles"""
    url = (
        f"{BASE_URL}/v2/aggs/ticker/{symbol}/range/1/{tf}/2023-01-01/2025-12-31"
        f"?limit={limit}&apiKey={API_KEY}"
    )
    return requests.get(url).json()

def get_options_chain(symbol: str, option_type: str = "call", days_out: int = 30):
    """Options chain snapshot"""
    url = f"{BASE_URL}/v3/snapshot/options/{symbol}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_news(symbol: str):
    """Latest news for a ticker"""
    url = f"{BASE_URL}/v2/reference/news?ticker={symbol}&limit=5&apiKey={API_KEY}"
    return requests.get(url).json()

def get_last_trade(symbol: str):
    """Last trade for a ticker"""
    url = f"{BASE_URL}/v2/last/trade/{symbol}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_ticker_details(symbol: str):
    """Company details for a ticker"""
    url = f"{BASE_URL}/v3/reference/tickers/{symbol}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_fundamentals(symbol: str):
    """Company fundamentals (financials)"""
    url = f"{BASE_URL}/vX/reference/financials?ticker={symbol.upper()}&limit=1&apiKey={API_KEY}"
    return requests.get(url).json()

def get_previous_day_bar(ticker: str):
    """Previous day OHLCV for a stock"""
    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/prev?apiKey={API_KEY}"
    return requests.get(url).json()

def get_single_stock_snapshot(ticker: str):
    """Snapshot for a single stock ticker"""
    url = f"{BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={API_KEY}"
    return requests.get(url).json()

# ---------------- Options endpoints ----------------

def get_all_option_contracts():
    """List all available option contracts"""
    url = f"{BASE_URL}/v3/reference/options/contracts?apiKey={API_KEY}"
    return requests.get(url).json()

def get_option_aggregates(options_ticker: str, multiplier: int, timespan: str, from_date: str, to_date: str):
    """Aggregate bars for an option contract"""
    url = (
        f"{BASE_URL}/v2/aggs/ticker/{options_ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        f"?apiKey={API_KEY}"
    )
    return requests.get(url).json()

def get_option_previous_day_bar(options_ticker: str):
    """Previous day OHLCV for an option contract"""
    url = f"{BASE_URL}/v2/aggs/ticker/{options_ticker}/prev?apiKey={API_KEY}"
    return requests.get(url).json()

def get_option_chain_snapshot(underlying_asset: str):
    """Snapshot of full option chain for an underlying"""
    url = f"{BASE_URL}/v3/snapshot/options/{underlying_asset}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_option_contract_snapshot(options_ticker: str):
    """
    Snapshot for a single option contract.
    ✅ Patched: validate contract exists before calling Polygon.
    """
    # Step 1: figure out underlying asset (e.g., AAPL from O:AAPL...)
    if not options_ticker.startswith("O:"):
        return {"error": "Invalid format. Must start with 'O:'."}

    try:
        underlying = options_ticker.split(":")[1][:4]  # crude parse (AAPL, TSLA, etc.)
    except Exception:
        return {"error": "Unable to parse underlying asset from ticker."}

    # Step 2: validate contract against chain
    chain_url = f"{BASE_URL}/v3/snapshot/options/{underlying}?apiKey={API_KEY}"
    chain_data = requests.get(chain_url).json()

    valid_contracts = []
    try:
        valid_contracts = [c["ticker"] for c in chain_data.get("results", [])]
    except Exception:
        pass

    if options_ticker not in valid_contracts:
        return {"error": f"Option contract {options_ticker} not found or expired."}

    # Step 3: fetch snapshot if valid
    url = f"{BASE_URL}/v2/snapshot/locale/us/markets/options/tickers/{options_ticker}?apiKey={API_KEY}"
    return requests.get(url).json()
