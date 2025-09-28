from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.openapi.utils import get_openapi
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

import pandas as pd
import numpy as np

app = FastAPI(title="MCP Server for Polygon.io")

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

@app.get("/options")
def options(symbol: str, type: str = "call", days_out: int = 30):
    return get_options_chain(symbol.upper(), option_type=type.lower(), days_out=days_out)

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

# ---------------- Stock + Options endpoints ----------------

@app.get("/previous-day-bar/{ticker}")
def previous_day_bar(ticker: str):
    return get_previous_day_bar(ticker.upper())

@app.get("/stock-snapshot/{ticker}")
def stock_snapshot(ticker: str):
    return get_single_stock_snapshot(ticker.upper())

@app.get("/all-option-contracts")
def all_option_contracts():
    return get_all_option_contracts()

@app.get("/option-aggregates/{options_ticker}")
def option_aggregates(options_ticker: str, multiplier: int, timespan: str, from_date: str, to_date: str):
    return get_option_aggregates(options_ticker.upper(), multiplier, timespan, from_date, to_date)

@app.get("/option-previous-day-bar/{options_ticker}")
def option_previous_day_bar(options_ticker: str):
    return get_option_previous_day_bar(options_ticker.upper())

@app.get("/option-contract-snapshot/{options_ticker}")
def option_contract_snapshot_route(options_ticker: str):
    """
    Wrapper for get_option_contract_snapshot with error handling.
    Returns 400 if invalid/expired contract is requested.
    """
    result = get_option_contract_snapshot(options_ticker.upper())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result

@app.get("/option-chain-snapshot/{underlying_asset}")
def option_chain_snapshot(underlying_asset: str):
    return get_option_chain_snapshot(underlying_asset.upper())

# ---------------- Indicators Endpoint ----------------

@app.get("/indicator/full-scan")
def full_indicator_scan(symbol: str, tf: str = "day", limit: int = 100):
    """Run full indicator scan: RSI, MACD, BB, VWAP, CMF, OBV, SMA50/200 w/ golden/death cross"""

    candles = get_candles(symbol.upper(), tf=tf, limit=limit)
    if "results" not in candles:
        return {"error": "No candle data returned"}

    closes = [c["c"] for c in candles["results"]]
    volumes = [c["v"] for c in candles["results"]]

    df = pd.DataFrame({"close": closes, "volume": volumes})

    # RSI
    delta = df["close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
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
           (df["close"].rolling(20).max() - df["close"])) / \
          (df["close"].rolling(20).max() - df["close"].rolling(20).min())
    mfv = mfm * df["volume"]
    df["CMF"] = mfv.rolling(20).sum() / df["volume"].rolling(20).sum()

    # OBV
    df["OBV"] = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()

    # SMA50 & SMA200
    df["SMA50"] = df["close"].rolling(window=50).mean()
    df["SMA200"] = df["close"].rolling(window=200).mean()

    golden_cross = None
    if df["SMA50"].iloc[-1] > df["SMA200"].iloc[-1]:
        golden_cross = "Golden Cross (Bullish)"
    elif df["SMA50"].iloc[-1] < df["SMA200"].iloc[-1]:
        golden_cross = "Death Cross (Bearish)"

    latest = df.iloc[-1].to_dict()

    return {
        "symbol": symbol.upper(),
        "RSI": round(float(latest["RSI"]), 2),
        "MACD": round(float(latest["MACD"]), 2),
        "Signal": round(float(latest["Signal"]), 2),
        "BollingerBands": {
            "upper": round(float(latest["BB_upper"]), 2),
            "lower": round(float(latest["BB_lower"]), 2),
        },
        "VWAP": round(float(latest["VWAP"]), 2),
        "CMF": round(float(latest["CMF"]), 2),
        "OBV": round(float(latest["OBV"]), 2),
        "SMA50": round(float(latest["SMA50"]), 2) if not np.isnan(latest["SMA50"]) else None,
        "SMA200": round(float(latest["SMA200"]), 2) if not np.isnan(latest["SMA200"]) else None,
        "TrendSignal": golden_cross,
    }

# ---------------- SSE ----------------

@app.get("/sse")
async def sse():
    async def event_generator():
        yield "data: connected\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ---------------- Custom OpenAPI ----------------

@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return JSONResponse(get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes
    ))
