import requests
import pandas as pd
import os
import numpy as np
from datetime import datetime

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histo"

INTERVAL_MAPPING = {
    "1h": "hour",
    "4h": "hour",
    "12h": "hour",
}

LIMIT_MAPPING = {
    "1h": 50,
    "4h": 50,
    "12h": 50,
}

MULTIPLIER_MAPPING = {
    "1h": 1,
    "4h": 4,
    "12h": 12,
}

def fetch_ohlcv(symbol: str, interval: str = "4h"):
    url_interval = INTERVAL_MAPPING.get(interval)
    aggregate = MULTIPLIER_MAPPING.get(interval, 4)
    limit = LIMIT_MAPPING.get(interval, 50)

    url = f"{BASE_URL}{url_interval}"
    params = {
        "fsym": symbol.upper(),
        "tsym": "USD",
        "limit": limit,
        "aggregate": aggregate,
        "api_key": CRYPTOCOMPARE_API_KEY,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()["Data"]["Data"]
        if not data:
            return None

        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)
        return df
    except Exception as e:
        print(f"❌ Failed to fetch OHLCV data: {e}")
        return None


def calculate_indicators(df):
    df["EMA20"] = df["close"].ewm(span=20).mean()
    df["EMA50"] = df["close"].ewm(span=50).mean()

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["MACD"] = df["close"].ewm(span=12).mean() - df["close"].ewm(span=26).mean()
    df["Signal"] = df["MACD"].ewm(span=9).mean()

    df["20sma"] = df["close"].rolling(window=20).mean()
    df["stddev"] = df["close"].rolling(window=20).std()
    df["UpperBand"] = df["20sma"] + 2 * df["stddev"]
    df["LowerBand"] = df["20sma"] - 2 * df["stddev"]

    df["TR"] = np.maximum(df["high"] - df["low"], np.maximum(abs(df["high"] - df["close"].shift()), abs(df["low"] - df["close"].shift())))
    df["ATR"] = df["TR"].rolling(window=14).mean()

    return df

def analyze_symbol(symbol: str, interval: str = "4h"):
    df = fetch_ohlcv(symbol, interval)
    if df is None or df.empty:
        return None

    df = calculate_indicators(df)
    latest = df.iloc[-1]

    signal = "Очікування сигналу"
    reason = ""

    if latest["RSI"] < 30 and latest["EMA20"] > latest["EMA50"]:
        signal = "LONG 📈"
        reason = "RSI < 30 та EMA20 > EMA50"
    elif latest["RSI"] > 70 and latest["EMA20"] < latest["EMA50"]:
        signal = "SHORT 📉"
        reason = "RSI > 70 та EMA20 < EMA50"

    return {
        "price": round(latest["close"], 2),
        "rsi": round(latest["RSI"], 2),
        "ema20": round(latest["EMA20"], 2),
        "ema50": round(latest["EMA50"], 2),
        "macd": round(latest["MACD"], 2),
        "macd_signal": round(latest["Signal"], 2),
        "upper_band": round(latest["UpperBand"], 2),
        "lower_band": round(latest["LowerBand"], 2),
        "atr": round(latest["ATR"], 2),
        "signal": signal,
        "reason": reason
    }