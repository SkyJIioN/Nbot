import requests
import pandas as pd
import numpy as np
from datetime import datetime

CRYPTOCOMPARE_API_KEY = "YOUR_CRYPTOCOMPARE_API_KEY"
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

headers = {
    "authorization": f"Apikey {CRYPTOCOMPARE_API_KEY}"
}

def fetch_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100):
    aggregate_map = {
        "1h": 1,
        "4h": 4,
        "12h": 12,
    }

    aggregate = aggregate_map.get(timeframe, 1)
    params = {
        "fsym": symbol.upper(),
        "tsym": "USD",
        "limit": limit,
        "aggregate": aggregate
    }
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data["Data"]["Data"]
    except Exception as e:
        print(f"❌ Failed to fetch OHLCV data: {e}")
        return None

def calculate_indicators(df: pd.DataFrame):
    df["SMA"] = df["close"].rolling(window=14).mean()
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

def generate_analysis(df: pd.DataFrame):
    latest = df.iloc[-1]
    rsi = latest["RSI"]
    sma = latest["SMA"]
    price = latest["close"]

    # Рекомендація
    recommendation = "Очікування сигналу"
    if rsi and sma:
        if rsi < 40 and price < sma:
            recommendation = "LONG"
        elif rsi > 60 and price > sma:
            recommendation = "SHORT"

    indicators_str = (
        f"🔍 Індикатори:\n"
        f"• RSI: {rsi:.2f} ({'Перепроданість' if rsi < 30 else 'Перекупленість' if rsi > 70 else 'Нейтрально'})\n"
        f"• SMA: {sma:.2f}\n"
        f"• Рекомендація: {recommendation}"
    )

    entry_price = price
    exit_price = price * (1.05 if recommendation == "LONG" else 0.95 if recommendation == "SHORT" else 1.0)

    return indicators_str, entry_price, exit_price, rsi, sma

async def analyze_crypto(symbol: str, timeframe: str):
    raw_data = fetch_ohlcv(symbol, timeframe)
    if not raw_data or len(raw_data) < 20:
        return None

    df = pd.DataFrame(raw_data)
    df = df[["time", "open", "high", "low", "close", "volumefrom"]]
    df.columns = ["time", "open", "high", "low", "close", "volume"]
    df["time"] = pd.to_datetime(df["time"], unit="s")

    df = calculate_indicators(df)

    if df[["RSI", "SMA"]].isnull().values.any():
        return None

    return generate_analysis(df)
