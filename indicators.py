import pandas as pd
import numpy as np

# =============== Utility ===============
def to_df(candles):
    """Convert Polygon candles JSON to DataFrame"""
    results = candles.get("results", [])
    if not results:
        return pd.DataFrame()
    df = pd.DataFrame(results)
    df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "t": "timestamp"}, inplace=True)
    return df


# =============== OBV ===============
def calc_obv(candles):
    df = to_df(candles)
    if df.empty:
        return {"error": "no data"}
    df["direction"] = np.sign(df["close"].diff())
    df["obv"] = (df["direction"] * df["volume"]).cumsum()
    return {"obv": float(df["obv"].iloc[-1])}


# =============== CMF ===============
def calc_cmf(candles, period=20):
    df = to_df(candles)
    if df.empty:
        return {"error": "no data"}
    df["mf_multiplier"] = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"]).replace(0, 1)
    df["mf_volume"] = df["mf_multiplier"] * df["volume"]
    cmf = df["mf_volume"].tail(period).sum() / df["volume"].tail(period).sum()
    return {"cmf": float(cmf)}


# =============== RSI (Momentum) ===============
def calc_rsi(candles, period=14):
    df = to_df(candles)
    if df.empty:
        return {"error": "no data"}
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss.replace(0, 1)
    rsi = 100 - (100 / (1 + rs))
    return {"rsi": float(rsi.iloc[-1])}


# =============== ADX (Trend Strength) ===============
def calc_adx(candles, period=14):
    df = to_df(candles)
    if df.empty or len(df) < period + 1:
        return {"error": "not enough data"}
    df["up_move"] = df["high"].diff()
    df["down_move"] = -df["low"].diff()
    df["+dm"] = np.where((df["up_move"] > df["down_move"]) & (df["up_move"] > 0), df["up_move"], 0.0)
    df["-dm"] = np.where((df["down_move"] > df["up_move"]) & (df["down_move"] > 0), df["down_move"], 0.0)
    tr = np.maximum(df["high"] - df["low"], np.maximum(abs(df["high"] - df["close"].shift()), abs(df["low"] - df["close"].shift())))
    atr = tr.rolling(period).mean()
    df["+di"] = 100 * (df["+dm"].rolling(period).mean() / atr)
    df["-di"] = 100 * (df["-dm"].rolling(period).mean() / atr)
    df["dx"] = (abs(df["+di"] - df["-di"]) / (df["+di"] + df["-di"])) * 100
    adx = df["dx"].rolling(period).mean()
    return {"adx": float(adx.iloc[-1])}


# =============== Bollinger Bands ===============
def calc_bollinger(candles, period=20, num_std=2):
    df = to_df(candles)
    if df.empty or len(df) < period:
        return {"error": "not enough data"}
    rolling_mean = df["close"].rolling(window=period).mean()
    rolling_std = df["close"].rolling(window=period).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return {
        "basis": float(rolling_mean.iloc[-1]),
        "upper": float(upper_band.iloc[-1]),
        "lower": float(lower_band.iloc[-1]),
        "zscore": float((df["close"].iloc[-1] - rolling_mean.iloc[-1]) / (rolling_std.iloc[-1] if rolling_std.iloc[-1] != 0 else 1))
    }


# =============== VWAP ===============
def calc_vwap(candles):
    df = to_df(candles)
    if df.empty:
        return {"error": "no data"}
    df["tp"] = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (df["tp"] * df["volume"]).sum() / df["volume"].sum()
    return {"vwap": float(vwap)}
