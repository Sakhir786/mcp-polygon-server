Absolutely — here’s a complete and professional `README.md` file for your project repo.

---

## ✅ `README.md` — MCP Polygon GPT Trading Server

````markdown
# 📈 MCP Polygon Server for GPT Stock Trading Agents

A lightweight FastAPI backend that connects to the **Polygon.io** API and powers a **GPT-4/5 stock trading agent**. It provides endpoints for real-time (delayed) quotes, candles, options, news, and more — and integrates with the **ChatGPT MCP Connector** to enable live, data-driven stock analysis.

---

## 🚀 Features

| Capability            | Endpoint              | Description                              |
|----------------------|------------------------|------------------------------------------|
| 🔍 Ticker Lookup      | `/symbol-lookup`       | Resolve user input to a valid stock ticker |
| 📈 Price Candles      | `/candles`             | Historical OHLCV data (day/minute)       |
| 📰 News Sentiment     | `/news`                | Latest news articles for a ticker        |
| 🎯 Options Chain      | `/options`             | Call/Put options ~30 days out            |
| 💬 Quote Snapshot     | `/quote`               | Last known quote (bid/ask/last)          |
| 🧾 Last Trade         | `/last-trade`          | Most recent trade price and volume       |
| 🏢 Ticker Metadata    | `/ticker-details`      | Sector, industry, exchange, etc.         |
| 🔄 SSE Keep Alive     | `/sse`                 | Maintains GPT MCP connection             |

---

## 🤖 Powered by

- [FastAPI](https://fastapi.tiangolo.com/)
- [Polygon.io](https://polygon.io/)
- [OpenAI GPTs + MCP Connector](https://platform.openai.com/)

---

## 🛠️ Setup & Deployment

### 1. 🔐 Create `.env` file

Create a `.env` file in the root directory with your Polygon API key:

```env
POLYGON_API_KEY=YOUR_API_KEY_HERE
````

---

### 2. 📦 Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. 🚀 Run the server locally

```bash
uvicorn main:app --reload --port 10000
```

The API will be live at: `http://localhost:10000`

---

### 4. 🌐 Render Deployment (Optional)

If you're using [Render.com](https://render.com):

* Include `render.yaml` in the root.
* Render will auto-install using `requirements.txt`.
* Set the environment variable `POLYGON_API_KEY`.

---

## 📡 Endpoints Overview

### 🔍 `/symbol-lookup?query=AAPL`

Returns all matching tickers for a company name or ticker.

---

### 📈 `/candles?symbol=AAPL&tf=day&limit=90`

Returns 90 days of OHLCV data for trend analysis.

---

### 📰 `/news?symbol=AAPL`

Fetches 5 latest news articles for the stock.

---

### 🎯 `/options?symbol=AAPL&type=call&days_out=30`

Returns near-term call/put option contracts.

---

### 💬 `/quote?symbol=AAPL`

Fetches delayed quote info (bid, ask, last price).

---

### 🧾 `/last-trade?symbol=AAPL`

Returns the last trade (price, volume, timestamp).

---

### 🏢 `/ticker-details?symbol=AAPL`

Returns metadata (sector, exchange, market cap).

---

### 🔄 `/sse`

Streaming endpoint to maintain GPT connector session.

---

## 📦 File Structure

```
.
├── main.py              # FastAPI route definitions
├── polygon_client.py    # API logic layer
├── requirements.txt     # Python dependencies
├── .env                 # Your API key (not committed)
├── render.yaml          # Render.com deployment config
└── README.md            # This file
```

---

## 🤖 GPT Integration (MCP Connector)

This backend is designed to connect with an **MCP-enabled GPT agent** via OpenAI's GPT builder.

Your GPT agent will use the following flow:

1. `/symbol-lookup` → resolve user input
2. `/candles` → get price trend
3. `/news` → get sentiment
4. `/options` → suggest options strategies
5. `/quote`, `/last-trade` → get latest pricing
6. `/ticker-details` → use context in analysis
7. Format reply → send strategy back to user

---

## 🧠 Example Strategy Output

```
📊 Stock Analysis: AAPL
📈 Trend: Bullish
💵 Current Price: $189.23
📰 News Sentiment: Positive
🏢 Sector: Technology | Market Cap: $3T

🎯 Top Options Picks
1. Strike $190 - Expiry 2025-10-18
2. Strike $195 - Expiry 2025-10-18

📈 Strategy
Price is in breakout, strong sentiment, and solid call volume.
Consider buying the $190 call and watch volume on dips.
```

---

## 🧑‍💻 Author

Built by [Your Name] with GPT as a data copilot
MCP + Polygon.io = GPT-powered stock analysis ⚡

---

## 📜 License

MIT License. Use freely, but credit the project!

```

---

✅ Want it in a `.md` file? I can generate a downloadable file or push to your repo.

Let me know if you want me to:

- Add custom screenshots
- Write a one-line `setup.sh`
- Generate the OpenAPI JSON schema export

You're officially production-ready. Let’s launch it. 🚀
```
