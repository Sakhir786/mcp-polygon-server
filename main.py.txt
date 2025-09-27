from fastapi import FastAPI
from polygon_client import (
    get_symbol_lookup,
    get_candles,
    get_options_chain,
    get_news
)

app = FastAPI(title="MCP Server for Polygon.io")

@app.get("/")
def root():
    return {"message": "MCP Server is running."}

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
