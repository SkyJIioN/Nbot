# services/market_data.py

import os
import requests
import pandas as pd

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

INTERVAL_MAP = {
    "1h": "60",
    "4h": "240",
    "12h": "720"
}

def fetch_ohlcv(symbol: str, timeframe: str = "4h", limit: int = 100):
    symbol = symbol.upper()
    if timeframe not in INTERVAL_MAP:
        timeframe = "4h"

    aggregate = INTERVAL_MAP[timeframe]
    url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={symbol}&tsym=USDT&limit={limit}&aggregate={aggregate}"

    headers = {"authorization": f"Apikey {CRYPTOCOMPARE_API_KEY}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    if data["Response"] != "Success":
        raise ValueError(f"❌ Помилка завантаження OHLCV: {data.get('Message')}")

    df = pd.DataFrame(data["Data"]["Data"])
    if df.empty:
        raise ValueError("❌ Порожні дані для графіку")

    df["timestamp"] = pd.to_datetime(df["time"], unit="s")
    return df

def calculate_indicators(df: pd.DataFrame):
    df["SMA"] = df["close"].rolling(window=20).mean()
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

async def analyze_crypto(symbol: str, timeframe: str = "4h") -> str:
    try:
        df = fetch_ohlcv(symbol, timeframe)
        df = calculate_indicators(df)

        current_price = df["close"].iloc[-1]
        sma = df["SMA"].iloc[-1]
        rsi = df["RSI"].iloc[-1]

        recommendation = "🔍 Аналіз:\n"
        recommendation += f"{symbol.upper()} на {timeframe.upper()}\n"
        recommendation += f"Ціна: ${current_price:.2f}\n"
        recommendation += f"📉 SMA (20): {sma:.2f}\n"
        recommendation += f"📊 RSI: {rsi:.2f}\n"

        if rsi < 30:
            entry = current_price * 0.99
            exit = current_price * 1.05
            recommendation += "✅ Рекомендація: Відкрити LONG\n"
            recommendation += f"🎯 Точка входу: ~${entry:.2f}\n"
            recommendation += f"🎯 Точка виходу: ~${exit:.2f}"
        elif rsi > 70:
            entry = current_price * 1.01
            exit = current_price * 0.95
            recommendation += "✅ Рекомендація: Відкрити SHORT\n"
            recommendation += f"🎯 Точка входу: ~${entry:.2f}\n"
            recommendation += f"🎯 Точка виходу: ~${exit:.2f}"
        else:
            recommendation += "⏳ Очікуйте кращої точки входу."

        return recommendation
    except Exception as e:
        print("❌", e)
        return None