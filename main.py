from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from polygon_client import (
    get_symbol_lookup,
    get_candles,
    get_options_chain,
    get_news,
    get_quote,
    get_last_trade,
    get_ticker_details,
    get_fundamentals,
    get_earnings
)
from fastapi.openapi.utils import get_openapi

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

@app.get("/quote")
def quote(symbol: str):
    return get_quote(symbol.upper())

@app.get("/last-trade")
def last_trade(symbol: str):
    return get_last_trade(symbol.upper())

@app.get("/ticker-details")
def ticker_details(symbol: str):
    return get_ticker_details(symbol.upper())

@app.get("/fundamentals")
def fundamentals(symbol: str):
    return get_fundamentals(symbol.upper())

@app.get("/earnings")
def earnings(symbol: str):
    return get_earnings(symbol.upper())

@app.get("/sse")
async def sse():
    async def event_generator():
        yield "data: connected\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return JSONResponse(get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes
    ))
