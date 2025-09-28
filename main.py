from fastapi import FastAPI
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
    result = get_option_contract_snapshot(options_ticker.upper())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result

@app.get("/option-chain-snapshot/{underlying_asset}")
def option_chain_snapshot(underlying_asset: str):
    return get_option_chain_snapshot(underlying_asset.upper())

# ---------------- Indicators ----------------

@app.get("/indicator/full-scan/{ticker}")
def full_scan(ticker: str, limit: int = 100):
    """Run full indicator suite (OBV, CMF, RSI, ADX, Bollinger Bands, VWAP)"""
    data = get_candles(ticker.upper(), tf="day", limit=limit)

    if "results" not in data:
        return {"error": "No candle data found."}

    df = pd.DataFrame(data["results"])
    df["date"] = pd.to_datetime(df["t"], unit="ms")
    df.set_index("date", inplace=True)

    # --- Indicators ---
    # OBV
    df["OBV"] = (np.sign(df["c"].diff()) * df["v"]).fillna(0).cumsum()

    # CMF (Chaikin Money Flow)
    mf_mult = ((df["c"] - df["l"]) - (df["h"] - df["c"])) / (df["h"] - df["l"])
    df["CMF"] = (mf_mult * df["v"]).rolling(20).sum() / df["v"].rolling(20).sum()

    # RSI
    delta = df["c"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # ADX
    df["+DM"] = np.where((df["h"].diff() > df["l"].diff()) & (df["h"].diff() > 0), df["h"].diff(), 0)
    df["-DM"] = np.where((df["l"].diff() > df["h"].diff()) & (df["l"].diff() > 0), df["l"].diff(), 0)
    df["+DI"] = 100 * (df["+DM"].ewm(span=14).mean() / df["v"])
    df["-DI"] = 100 * (df["-DM"].ewm(span=14).mean() / df["v"])
    df["ADX"] = (abs(df["+DI"] - df["-DI"]) / (df["+DI"] + df["-DI"])) * 100

    # Bollinger Bands
    df["MA20"] = df["c"].rolling(20).mean()
    df["STD20"] = df["c"].rolling(20).std()
    df["Upper"] = df["MA20"] + (2 * df["STD20"])
    df["Lower"] = df["MA20"] - (2 * df["STD20"])

    # VWAP
    df["VWAP"] = (df["v"] * (df["h"] + df["l"] + df["c"]) / 3).cumsum() / df["v"].cumsum()

    latest = df.iloc[-1]

    return {
        "symbol": ticker.upper(),
        "indicators": {
            "OBV": float(latest["OBV"]),
            "CMF": float(latest["CMF"]),
            "RSI": float(latest["RSI"]),
            "ADX": float(latest["ADX"]),
            "Bollinger": {
                "upper": float(latest["Upper"]),
                "lower": float(latest["Lower"]),
                "ma20": float(latest["MA20"]),
                "price_vs_band": "above_upper" if latest["c"] > latest["Upper"] else
                                 "below_lower" if latest["c"] < latest["Lower"] else "inside"
            },
            "VWAP": {
                "value": float(latest["VWAP"]),
                "price_vs_vwap": "above" if latest["c"] > latest["VWAP"] else "below"
            }
        }
    }

# ---------------- SSE (for streaming) ----------------

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
