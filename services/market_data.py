import os
import requests
import pandas as pd
import numpy as np

COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")
HEADERS = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY,
}
BASE_URL = "https://pro-api.coinmarketcap.com"


def fetch_ohlcv(symbol: str, interval: str = "4h", limit: int = 100):
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": f"{symbol}USDT", "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close",
            "volume", "close_time", "quote_asset_volume",
            "num_trades", "taker_buy_base_volume",
            "taker_buy_quote_volume", "ignore"
        ])
        df["close"] = df["close"].astype(float)
        return df
    except Exception as e:
        print(f"Failed to fetch OHLCV data: {e}")
        return None


def calculate_rsi(close_prices, period: int = 14):
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_sma(close_prices, period: int = 14):
    return close_prices.rolling(window=period).mean()


def analyze_symbol(symbol: str):
    df = fetch_ohlcv(symbol)
    if df is None or df.empty:
        return f"Не вдалося отримати історичні дані для {symbol}."

    df["rsi"] = calculate_rsi(df["close"])
    df["sma"] = calculate_sma(df["close"])

    last_price = df["close"].iloc[-1]
    last_rsi = df["rsi"].iloc[-1]
    last_sma = df["sma"].iloc[-1]

    recommendation = "🔎 Нейтрально"
    entry = round(last_price, 2)
    take_profit = round(last_price * 1.02, 2)
    stop_loss = round(last_price * 0.98, 2)

    if last_rsi < 30 and last_price > last_sma:
        recommendation = "🟢 LONG позиція"
    elif last_rsi > 70 and last_price < last_sma:
        recommendation = "🔴 SHORT позиція"

    return (
        f"📊 *Аналіз {symbol.upper()}*\n"
        f"Ціна: `{entry} USDT`\n"
        f"RSI: `{last_rsi:.2f}`\n"
        f"SMA: `{last_sma:.2f}`\n"
        f"Рекомендація: *{recommendation}*\n"
        f"Точка входу: `{entry}`\n"
        f"Take-Profit: `{take_profit}`\n"
        f"Stop-Loss: `{stop_loss}`"
    )