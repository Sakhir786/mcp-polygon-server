# 📈 MCP Polygon GPT + TradePilot Engine  
### (Render Deployment Edition)

A production-grade **FastAPI backend** built for **real-time trading intelligence**, integrating **Polygon.io data** with GPT-driven decision logic.  
Deployed seamlessly on **Render.com**, this server powers the **TradePilot GPT Agent** — providing structured indicator analytics, signal generation, and multi-layer strategy execution.

---

## 🚀 Core Features

| Capability | Endpoint | Description |
|-------------|-----------|-------------|
| 🔍 Ticker Lookup | `/symbol-lookup` | Resolve company names to valid tickers |
| 📈 Price Candles | `/candles` | Pull OHLCV data for any timeframe |
| 📰 News Feed | `/news` | Latest market and sentiment-tagged headlines |
| 🎯 Options Chain | `/options` | Retrieves active call/put contracts |
| 💬 Quote Snapshot | `/quote` | Live bid/ask/last price data |
| 🧾 Last Trade | `/last-trade` | Latest executed trade and volume |
| 🏢 Company Info | `/ticker-details` | Metadata (sector, market cap, etc.) |
| ⚙️ Engine Analysis | `/engine/analyze` | Runs multi-layer indicator engine |
| 🧠 Signal Summary | `/engine/signal-summary` | Returns overall technical bias |
| 🔄 SSE | `/sse` | Keeps GPT MCP session active |

---

## ☁️ Render Deployment

This project is built for **Render.com** — minimal setup, automatic scaling, and secure environment management.

### 1️⃣ Deploy on Render

1. Push this repository to **GitHub**.
2. Go to your [Render Dashboard](https://render.com).
3. Click **“New → Web Service”**.
4. Connect your GitHub repo → Render detects it’s a **Python (FastAPI)** app automatically.

---

### 2️⃣ Add Environment Variables

In Render → **Environment** tab → click **Add Variable**:

| Key | Value |
|------|-------|
| `POLYGON_API_KEY` | Your Polygon.io API key |
| `PORT` | `10000` |
| `PYTHON_VERSION` | `3.11` |

---

### 3️⃣ Add `render.yaml` (already included)

Your current Render config file should look like this:

```yaml
# 📦 render.yaml — Deployment Configuration
services:
  - type: web
    name: tradepilot-mcp-server
    env: python
    plan: starter
    region: oregon

    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements.txt

    startCommand: |
      uvicorn main:app --host 0.0.0.0 --port 10000

    envVars:
      - key: POLYGON_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11
      - key: PORT
        value: 10000

    autoDeploy: true
    healthCheckPath: /
    disk:
      name: engine-cache
      mountPath: /mnt/data
      sizeGB: 2
✅ This configuration:

Installs dependencies automatically

Exposes your FastAPI app at https://tradepilot-mcp-server.onrender.com

Keeps your .env keys secure

Creates a small persistent disk for cached indicator data

4️⃣ File Structure
After adding engine_router.py and tradepilot_engine/, your directory should look like this:

bash
Copy code
.
├── .env
├── README.md
├── config.py
├── indicators.py
├── main.py
├── polygon_client.py
├── engine_router.py            # ⚙️ Handles /engine endpoints
├── render.yaml
├── requirements.txt
└── tradepilot_engine/          # 🧠 Multi-layer technical engine
    ├── layer_1_momentum/
    ├── layer_2_volume/
    ├── layer_3_divergence/
    ├── layer_4_volume_strength/
    ├── layer_5_trend/
    ├── layer_6_structure/
    ├── layer_7_liquidity/
    ├── layer_8_volatility_regime/
    ├── layer_9_confirmation/
    └── layer_10_candle_intelligence/
⚙️ TradePilot Engine Overview
The TradePilot Engine is modular and indicator-driven.
Each layer corresponds to one analytical domain:

Layer	Category	Example Indicators	Purpose
1️⃣	Momentum	RSI Divergence, MACD, Momentum Oscillators	Detects acceleration & exhaustion
2️⃣	Volume	OBV, AD, CMF, CDV	Tracks institutional volume flow
3️⃣	Divergence	Delta Divergence Detector	Confirms price–flow divergence
4️⃣	Volume Strength	RVOL, Volume Spike	Detects unusual accumulation
5️⃣	Trend	ADX/DMI, SuperTrend, ATR Bands	Confirms dominant direction
6️⃣	Structure	CHoCH/BOS, FVG	Smart money structure mapping
7️⃣	Liquidity	Liquidity Concepts	Detects sweep zones & stops
8️⃣	Volatility	ATR Percentile Zones	Defines current volatility regime
9️⃣	Confirmation	MTF Continuity	Confirms cross-TF directional bias
🔟	Candle Intelligence	Candle Pattern Detector	Validates entries via candle logic

🧠 Endpoints Overview
🔹 /engine/analyze?symbol=AAPL&tf=15m
Runs all 10 layers and returns combined signal map.

🔹 /engine/signal-summary?symbol=AAPL
Returns summarized bias:

json
Copy code
{
  "symbol": "AAPL",
  "signal_summary": {
    "momentum_bias": "Bullish",
    "trend_strength": 0.81,
    "volume_pressure": 0.67,
    "volatility_regime": "Normal",
    "overall_confidence": 0.84
  }
}
🔹 /engine/raw/layer_3_divergence
Fetches data from a specific layer for debugging.

🧪 Local Testing (Optional)
bash
Copy code
pip install -r requirements.txt
uvicorn main:app --reload --port 10000
Then open:

arduino
Copy code
http://127.0.0.1:10000/docs
🧑‍💻 Author
Built by [Your Name] with GPT-5 as a live data copilot.
MCP + Polygon.io + Render + TradePilot Engine = autonomous, data-driven trade intelligence ⚡

📜 License
MIT License.
