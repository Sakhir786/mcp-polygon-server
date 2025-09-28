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

def get_candles(symbol: str, tf: str = "day", limit: int = 90):
    url = (
        f"{BASE_URL}/v2/aggs/ticker/{symbol}/range/1/{tf}/2023-01-01/2025-12-31"
        f"?limit={limit}&apiKey={API_KEY}"
    )
    return requests.get(url).json()

def get_options_chain(symbol: str, option_type: str = "call", days_out: int = 30):
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

def get_all_option_contracts():
    url = f"{BASE_URL}/v3/reference/options/contracts?apiKey={API_KEY}"
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

def get_option_chain_snapshot(underlying_asset: str):
    url = f"{BASE_URL}/v3/snapshot/options/{underlying_asset}?apiKey={API_KEY}"
    return requests.get(url).json()

def get_option_contract_snapshot(options_ticker: str, expiry_bucket: str = "30d"):
    """
    Snapshot for a single option contract with expiry filtering.
    expiry_bucket: otd, 7d, 30d, 90d, 365d, 730d
    """
    if not options_ticker.startswith("O:"):
        return {"error": "Invalid format. Must start with 'O:'."}

    try:
        underlying = options_ticker.split(":")[1][:4]  # crude parse
    except Exception:
        return {"error": "Unable to parse underlying asset from ticker."}

    # Step 1: fetch option chain
    chain_url = f"{BASE_URL}/v3/snapshot/options/{underlying}?apiKey={API_KEY}"
    chain_data = requests.get(chain_url).json()

    contracts = chain_data.get("results", [])
    if not contracts:
        return {"error": "No contracts found for this underlying."}

    # Step 2: filter by expiry bucket
    today = datetime.utcnow().date()
    expiry_ranges = {
        "otd": today,
        "7d": today + timedelta(days=7),
        "30d": today + timedelta(days=30),
        "90d": today + timedelta(days=90),
        "365d": today + timedelta(days=365),
        "730d": today + timedelta(days=730),
    }

    max_expiry = expiry_ranges.get(expiry_bucket, today + timedelta(days=30))

    valid_contracts = [
        c for c in contracts
        if "expiration_date" in c
        and datetime.fromisoformat(c["expiration_date"]).date() >= today
        and datetime.fromisoformat(c["expiration_date"]).date() <= max_expiry
    ]

    # Step 3: find matching contract in filtered list
    if not any(c["ticker"] == options_ticker for c in valid_contracts):
        return {"error": f"Option {options_ticker} not found in bucket {expiry_bucket}"}

    # Step 4: return snapshot
    url = f"{BASE_URL}/v2/snapshot/locale/us/markets/options/tickers/{options_ticker}?apiKey={API_KEY}"
    return requests.get(url).json()
