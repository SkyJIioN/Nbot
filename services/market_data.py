import requests
import pandas as pd
from datetime import datetime
import os

API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

def get_ohlcv(symbol: str, timeframe: str = "4h") -> pd.DataFrame:
    mapping = {
        "1h": ("hour", 1),
        "4h": ("hour", 4),
        "12h": ("hour", 12),
        "1d": ("day", 1),
    }

    if timeframe not in mapping:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    unit, aggregate = mapping[timeframe]

    # fallback у випадку занадто великого aggregate
    if (unit == "hour" and aggregate > 24) or (unit == "day" and aggregate > 30):
        aggregate = 1

    url = f"https://min-api.cryptocompare.com/data/v2/histo{unit}?fsym={symbol.upper()}&tsym=USDT&limit=100&aggregate={aggregate}&api_key={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()["Data"]["Data"]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch OHLCV data: {e}")

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["time"], unit="s")
    df.set_index("timestamp", inplace=True)

    return df[["open", "high", "low", "close", "volumeto"]]

def calculate_indicators(df: pd.DataFrame) -> dict:
    df["sma"] = df["close"].rolling(window=14).mean()
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))
    return {
        "rsi": df["rsi"].iloc[-1],
        "sma": df["sma"].iloc[-1],
        "current_price": df["close"].iloc[-1],
    }

def analyze_symbol(symbol: str, timeframe: str = "4h") -> tuple:
    try:
        df = get_ohlcv(symbol, timeframe)
        indicators = calculate_indicators(df)

        rsi = indicators["rsi"]
        sma = indicators["sma"]
        price = indicators["current_price"]

        if pd.isna(rsi) or pd.isna(sma):
            return ("⚠️ Недостатньо даних для аналізу.", None, None, None)

        signal = ""
        if rsi < 30 and price > sma:
            signal = "🟢 Рекомендовано LONG"
        elif rsi > 70 and price < sma:
            signal = "🔴 Рекомендовано SHORT"
        else:
            signal = "🟡 Очікування сигналу"

        entry = round(price, 2)
        exit_1 = round(entry * 1.03, 2)
        exit_2 = round(entry * 1.05, 2)

        text = (
            f"📈 RSI: {round(rsi, 2)}\n"
            f"📊 SMA(14): {round(sma, 2)}\n"
            f"💰 Поточна ціна: ${entry}\n\n"
            f"{signal}\n"
            f"🔽 Вхід: ${entry}\n"
            f"🔼 Вихід: ${exit_1} — ${exit_2}"
        )

        return text, entry, rsi, sma

    except Exception as e:
        return (f"❌ Не вдалося отримати дані для {symbol.upper()}: {str(e)}", None, None, None)
analyze_crypto = analyze_symbol