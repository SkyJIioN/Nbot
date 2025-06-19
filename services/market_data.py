import os
import requests
import pandas as pd
import numpy as np

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

def fetch_ohlcv(symbol: str, limit: int = 100) -> pd.DataFrame | None:
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    params = {
        "fsym": symbol.upper(),
        "tsym": "USDT",
        "limit": limit,
        "aggregate": 4,  # 4H таймфрейм
        "api_key": CRYPTOCOMPARE_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["Response"] != "Success":
            print(f"❌ API error for {symbol}: {data.get('Message')}")
            return None

        df = pd.DataFrame(data["Data"]["Data"])
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)
        return df
    except Exception as e:
        print(f"❌ Failed to fetch OHLCV data for {symbol}: {e}")
        return None

def calculate_indicators(df: pd.DataFrame) -> dict:
    indicators = {}

    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    exp1 = df["close"].ewm(span=12, adjust=False).mean()
    exp2 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = exp1 - exp2
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    df["sma20"] = df["close"].rolling(window=20).mean()
    df["stddev"] = df["close"].rolling(window=20).std()
    df["upper_band"] = df["sma20"] + 2 * df["stddev"]
    df["lower_band"] = df["sma20"] - 2 * df["stddev"]

    df["atr"] = (df["high"] - df["low"]).rolling(window=14).mean()

    latest = df.iloc[-1]

    indicators.update({
        "price": latest["close"],
        "rsi": round(latest["rsi"], 2),
        "ema20": round(latest["ema20"], 2),
        "ema50": round(latest["ema50"], 2),
        "macd": round(latest["macd"], 4),
        "macd_signal": round(latest["macd_signal"], 4),
        "upper_band": round(latest["upper_band"], 2),
        "lower_band": round(latest["lower_band"], 2),
        "atr": round(latest["atr"], 2)
    })

    return indicators

def analyze_symbol(symbol: str) -> dict | None:
    df = fetch_ohlcv(symbol)
    if df is None or df.empty:
        return None

    indicators = calculate_indicators(df)

    # Проста логіка сигналу:
    rsi = indicators["rsi"]
    macd = indicators["macd"]
    macd_signal = indicators["macd_signal"]
    price = indicators["price"]

    signal = "Очікування"
    reason = []

    if rsi < 30 and macd > macd_signal:
        signal = "📈 LONG"
        reason.append("RSI в зоні перепроданості, MACD вище сигнальної лінії")
    elif rsi > 70 and macd < macd_signal:
        signal = "📉 SHORT"
        reason.append("RSI в зоні перекупленості, MACD нижче сигнальної лінії")

    indicators["signal"] = signal
    indicators["reason"] = "; ".join(reason)

    return indicators