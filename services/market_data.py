# services/market_data.py

import requests
import pandas as pd
from datetime import datetime, timedelta
import os

CMC_API_KEY = os.getenv("CMC_API_KEY")
CMC_BASE_URL = "https://pro-api.coinmarketcap.com"

headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": CMC_API_KEY
}

def get_ohlcv(symbol: str):
    """Отримує OHLCV дані за 4 години (24 останніх свічки = 4 дні)"""
    url = f"{CMC_BASE_URL}/cryptocurrency/ohlcv/historical"
    params = {
        "symbol": symbol.upper(),
        "convert": "USD",
        "time_start": (datetime.utcnow() - timedelta(days=4)).isoformat(),
        "interval": "4h"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Не вдалося отримати OHLCV: {response.text}")
    data = response.json()["data"]["quotes"]
    df = pd.DataFrame([{
        "time": q["time_open"],
        "open": q["quote"]["USD"]["open"],
        "high": q["quote"]["USD"]["high"],
        "low": q["quote"]["USD"]["low"],
        "close": q["quote"]["USD"]["close"]
    } for q in data])
    df["time"] = pd.to_datetime(df["time"])
    return df

def calculate_rsi(close_prices, period=14):
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_symbol(symbol: str) -> str:
    try:
        df = get_ohlcv(symbol)
        df["SMA20"] = df["close"].rolling(window=20).mean()
        df["RSI"] = calculate_rsi(df["close"])
        latest = df.iloc[-1]

        sma_trend = "вище" if latest["close"] > latest["SMA20"] else "нижче"
        rsi_value = latest["RSI"]

        rsi_sentiment = ""
        if rsi_value < 30:
            rsi_sentiment = "перепроданість (можлива LONG позиція)"
        elif rsi_value > 70:
            rsi_sentiment = "перекупленість (можлива SHORT позиція)"
        else:
            rsi_sentiment = "нейтральна зона (варто зачекати)"

        entry_price = round(latest["close"], 2)
        exit_price = round(entry_price * 1.05, 2) if "LONG" in rsi_sentiment else round(entry_price * 0.95, 2)

        return (
            f"🔍 Аналіз {symbol.upper()} (4H):\n"
            f"Поточна ціна: ${entry_price}\n"
            f"Ціна {sma_trend} SMA20\n"
            f"RSI: {rsi_value:.2f} — {rsi_sentiment}\n"
            f"🎯 Рекомендована позиція: {'LONG' if 'LONG' in rsi_sentiment else 'SHORT' if 'SHORT' in rsi_sentiment else 'Очікування'}\n"
            f"📈 Точка входу: ${entry_price}\n"
            f"📉 Точка виходу: ${exit_price}"
        )
    except Exception as e:
        return f"❌ Помилка аналізу {symbol.upper()}: {e}"