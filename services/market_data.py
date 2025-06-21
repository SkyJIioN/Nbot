import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime

API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

async def analyze_crypto(symbol: str, timeframe: str = "1h"):
    symbol = symbol.upper()
    aggregate_mapping = {"1h": 1, "4h": 4, "12h": 12}
    aggregate = aggregate_mapping.get(timeframe, 1)

    params = {
        "fsym": symbol,
        "tsym": "USDT",
        "limit": 50,
        "aggregate": aggregate,
        "api_key": API_KEY,
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        ohlcv = data["Data"]["Data"]
    
        if not ohlcv or len(ohlcv) < 20:
            return None

        df = pd.DataFrame(ohlcv)
        df["close"] = df["close"].astype(float)

        df["sma"] = df["close"].rolling(window=20).mean()
        delta = df["close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=14).mean()
        avg_loss = pd.Series(loss).rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["rsi"] = 100 - (100 / (1 + rs))

        current_price = df["close"].iloc[-1]
        sma = df["sma"].iloc[-1]
        rsi = df["rsi"].iloc[-1]

        signal = "⚪️ Очікування сигналу"
        entry_price = current_price
        exit_price = None

        if rsi < 30 and current_price > sma:
            signal = "🟢 LONG сигнал"
            exit_price = current_price * 1.03
        elif rsi > 70 and current_price < sma:
            signal = "🔴 SHORT сигнал"
            exit_price = current_price * 0.97

        indicators_str = (
            f"{signal}\n"
            f"💰 Вхід: {entry_price:.2f}$"
        )

        return indicators_str, entry_price, exit_price, rsi, sma

    except Exception as e:
        print(f"Failed to fetch OHLCV data: {e}")
        return None
if pd.isna(rsi) or pd.isna(sma):
            return None

        return indicators_str, entry_price, exit_price, rsi, sma