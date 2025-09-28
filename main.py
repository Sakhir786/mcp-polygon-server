from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, StreamingResponse
from polygon_client import (
    get_symbol_lookup,
    get_candles,
    get_options_chain,
    get_news,
    get_last_trade,
    get_ticker_details,
    get_fundamentals,
    get_previous_day_bar,
    get_single_stock_snapshot,
    get_all_option_contracts,
    get_option_aggregates,
    get_option_previous_day_bar,
    get_option_contract_snapshot,
    get_option_chain_snapshot,
)
from fastapi.openapi.utils import get_openapi
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

app = FastAPI(title="MCP Server for Polygon.io")

# ---------------- Root ----------------

@app.get("/")
def root():
    return {"message": "MCP Server is running."}

# ---------------- Core endpoints ----------------

@app.get("/symbol-lookup")
def symbol_lookup(query: str):
    return get_symbol_lookup(query)

@app.get("/candles")
def candles(symbol: str, tf: str = "day", limit: int = 90):
    return get_candles(symbol.upper(), tf=tf, limit=limit)

@app.get("/news")
def news(symbol: str):
    return get_news(symbol.upper())

@app.get("/last-trade")
def last_trade(symbol: str):
    return get_last_trade(symbol.upper())

@app.get("/ticker-details")
def ticker_details(symbol: str):
    return get_ticker_details(symbol.upper())

@app.get("/fundamentals")
def fundamentals(symbol: str):
    return get_fundamentals(symbol.upper())

# ---------------- Stock endpoints ----------------

@app.get("/previous-day-bar/{ticker}")
def previous_day_bar(ticker: str):
    return get_previous_day_bar(ticker.upper())

@app.get("/stock-snapshot/{ticker}")
def stock_snapshot(ticker: str):
    return get_single_stock_snapshot(ticker.upper())

# ---------------- Options endpoints with expiry filtering ----------------

def filter_by_expiry(results: list, expiry_bucket: str | None = None):
    """Filter options contracts between today and +2 years. Optionally narrow by bucket."""
    today = datetime.utcnow().date()
    max_date = today + timedelta(days=730)

    filtered = []
    for c in results:
        expiry = c.get("expiration_date")
        if not expiry:
            continue
        try:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        except Exception:
            continue
        if today <= expiry_date <= max_date:
            filtered.append(c)

    # Apply expiry bucket if given
    if expiry_bucket:
        bucket_days = {
            "otd": 0,
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "365d": 365,
            "730d": 730,
        }
        if expiry_bucket in bucket_days:
            cutoff = today + timedelta(days=bucket_days[expiry_bucket])
            filtered = [
                c for c in filtered
                if datetime.strptime(c["expiration_date"], "%Y-%m-%d").date() <= cutoff
            ]

    return filtered

@app.get("/options")
def options(symbol: str,
            type: str = "call",
            days_out: int = 30,
            expiry_bucket: str | None = Query(None, enum=["otd","7d","30d","90d","365d","730d"])):
    chain = get_options_chain(symbol.upper(), option_type=type.lower(), days_out=days_out)
    if "results" in chain:
        chain["results"] = filter_by_expiry(chain["results"], expiry_bucket)
    return chain

@app.get("/all-option-contracts")
def all_option_contracts(expiry_bucket: str | None = Query(None, enum=["otd","7d","30d","90d","365d","730d"])):
    contracts = get_all_option_contracts()
    if "results" in contracts:
        contracts["results"] = filter_by_expiry(contracts["results"], expiry_bucket)
    return contracts

@app.get("/option-aggregates/{options_ticker}")
def option_aggregates(options_ticker: str, multiplier: int, timespan: str, from_date: str, to_date: str):
    return get_option_aggregates(options_ticker.upper(), multiplier, timespan, from_date, to_date)

@app.get("/option-previous-day-bar/{options_ticker}")
def option_previous_day_bar(options_ticker: str):
    return get_option_previous_day_bar(options_ticker.upper())

@app.get("/option-contract-snapshot/{options_ticker}")
def option_contract_snapshot_route(options_ticker: str):
    """
    Wrapper for get_option_contract_snapshot with expiry filtering.
    Returns 400 if contract is expired or invalid.
    """
    result = get_option_contract_snapshot(options_ticker.upper())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)

    expiry = result.get("results", {}).get("expiration_date")
    if expiry:
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        today = datetime.utcnow().date()
        if expiry_date < today or expiry_date > today + timedelta(days=730):
            return JSONResponse(status_code=400, content={"error": "Expired or too far contract"})
    return result

@app.get("/option-chain-snapshot/{underlying_asset}")
def option_chain_snapshot_route(underlying_asset: str,
                                expiry_bucket: str | None = Query(None, enum=["otd","7d","30d","90d","365d","730d"])):
    chain = get_option_chain_snapshot(underlying_asset.upper())
    if "results" in chain:
        chain["results"] = filter_by_expiry(chain["results"], expiry_bucket)
    return chain

# ---------------- Indicator Full Scan ----------------

@app.get("/indicator/full-scan")
def full_indicator_scan(symbol: str, tf: str = "day", limit: int = 100):
    """Run a full indicator scan (RSI, MACD, BB, VWAP, CMF, OBV, SMA50/200)."""
    candles = get_candles(symbol.upper(), tf=tf, limit=limit)
    if "results" not in candles:
        return JSONResponse(status_code=400, content={"error": "No candle data"})

    closes = [c["c"] for c in candles["results"]]
    volumes = [c["v"] for c in candles["results"]]

    df = pd.DataFrame({"close": closes, "volume": volumes})

    # RSI
    delta = df["close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    sma20 = df["close"].rolling(window=20).mean()
    std20 = df["close"].rolling(window=20).std()
    df["BB_upper"] = sma20 + 2 * std20
    df["BB_lower"] = sma20 - 2 * std20

    # VWAP
    df["VWAP"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()

    # CMF
    mfm = ((df["close"] - df["close"].rolling(20).min()) -
           (df["close"].rolling(20).max() - df["close"])) / (
           df["close"].rolling(20).max() - df["close"].rolling(20).min())
    mfv = mfm * df["volume"]
    df["CMF"] = mfv.rolling(20).sum() / df["volume"].rolling(20).sum()

    # OBV
    df["OBV"] = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()

    # SMA 50 & 200
    df["SMA50"] = df["close"].rolling(window=50).mean()
    df["SMA200"] = df["close"].rolling(window=200).mean()
    golden_cross = bool(df["SMA50"].iloc[-1] > df["SMA200"].iloc[-1])
    death_cross = bool(df["SMA50"].iloc[-1] < df["SMA200"].iloc[-1])

    # Latest values
    latest = df.iloc[-1].to_dict()
    return {
        "symbol": symbol.upper(),
        "RSI": round(float(latest.get("RSI", 0)), 2),
        "MACD": round(float(latest.get("MACD", 0)), 2),
        "Signal": round(float(latest.get("Signal", 0)), 2),
        "BollingerBands": {
            "upper": round(float(latest.get("BB_upper", 0)), 2),
            "lower": round(float(latest.get("BB_lower", 0)), 2),
        },
        "VWAP": round(float(latest.get("VWAP", 0)), 2),
        "CMF": round(float(latest.get("CMF", 0)), 4),
        "OBV": round(float(latest.get("OBV", 0)), 2),
        "SMA50": round(float(latest.get("SMA50", 0)), 2),
        "SMA200": round(float(latest.get("SMA200", 0)), 2),
        "GoldenCross": golden_cross,
        "DeathCross": death_cross,
    }

# ---------------- SSE ----------------

@app.get("/sse")
async def sse():
    async def event_generator():
        yield "data: connected\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ---------------- OpenAPI ----------------

@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return JSONResponse(get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes
    ))
