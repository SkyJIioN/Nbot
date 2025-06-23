import requests
import pandas as pd
import numpy as np
from datetime import datetime

API_KEY = "ТВОЙ_API_KEY_CRYPTOCOMPARE"  # Заміни на свій реальний API ключ
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

def fetch_ohlcv_data(symbol: str, timeframe: str, limit: int = 100):
    params = {
        "fsym": symbol.upper(),
        "tsym": "USD",
        "limit": limit,
        "api_key": API_KEY
    }

    if timeframe == "1h":
        params["aggregate"] = 1
    elif timeframe == "4h":
        params["aggregate"] = 4
    elif timeframe == "12h":
        params["aggregate"] = 12
    else:
        print(f"❌ Невідомий таймфрейм: {timeframe}")
        return None

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data.get("Response") != "Success":
            print(f"❌ Помилка завантаження OHLCV: {data.get('Message')}")
            return None

        ohlcv = data["Data"]["Data"]
        if len(ohlcv) < 20:
            print(f"⚠️ Недостатньо OHLCV-даних: {len(ohlcv)} для {symbol} {timeframe}")
            return None

        df = pd.DataFrame(ohlcv)
        df["datetime"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("datetime", inplace=True)
        df["close"] = df["close"]
        return df

    except Exception as e:
        print(f"❌ Виняток при отриманні OHLCV: {e}")
        return None

def calculate_indicators(df):
    try:
        df["rsi"] = compute_rsi(df["close"])
        df["sma"] = df["close"].rolling(window=14).mean()
        df["ema"] = df["close"].ewm(span=14).mean()
        df["macd"] = df["close"].ewm(span=12).mean() - df["close"].ewm(span=26).mean()
        df["macd_signal"] = df["macd"].ewm(span=9).mean()
        return df
    except Exception as e:
        print(f"❌ Помилка при розрахунку індикаторів: {e}")
        return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_crypto(symbol: str, timeframe: str):
    df = fetch_ohlcv_data(symbol, timeframe)
    if df is None or df.empty:
        return None

    df = calculate_indicators(df)

    if len(df) < 20 or pd.isna(df["rsi"].iloc[-1]):
        print("⚠️ Недостатньо даних для аналізу.")
        return None

    latest = df.iloc[-1]

    rsi = latest["rsi"]
    sma = latest["sma"]
    ema = latest["ema"]
    macd = latest["macd"]
    macd_signal = latest["macd_signal"]
    current_price = latest["close"]

    # Рекомендація на основі RSI
    if rsi < 30:
        signal = "🟢 Перепроданість — можливий LONG"
    elif rsi > 70:
        signal = "🔴 Перекупленість — можливий SHORT"
    else:
        signal = "⚪️ Очікування сигналу"

    indicators_str = (
        f"🔍 Індикатори:\n"
        f"• RSI: {rsi:.2f} ({'Перепроданість' if rsi < 30 else 'Перекупленість' if rsi > 70 else 'Нейтрально'})\n"
        f"• SMA: {sma:.2f}\n"
        f"• EMA: {ema:.2f}\n"
        f"• MACD: {macd:.2f}, Signal: {macd_signal:.2f}\n"
        f"• Рекомендація: {signal}"
    )

    entry_price = float(current_price)
    exit_price = entry_price * 1.015 if rsi < 30 else entry_price * 0.985 if rsi > 70 else entry_price

    return indicators_str, entry_price, exit_price, rsi, sma, ema, macd, macd_signal