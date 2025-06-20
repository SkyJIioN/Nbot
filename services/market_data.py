import requests
import pandas as pd
import os

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

def fetch_ohlcv(symbol: str, timeframe: str = "4h", limit: int = 100):
    symbol = symbol.upper()
    url = "https://min-api.cryptocompare.com/data/v2/histohour"

    tf_map = {
        "1h": 1,
        "4h": 4,
        "12h": 12
    }

    aggregate = tf_map.get(timeframe, 4)

    params = {
        "fsym": symbol,
        "tsym": "USDT",
        "limit": limit,
        "aggregate": aggregate,
        "api_key": CRYPTOCOMPARE_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["Response"] != "Success":
            raise Exception("Invalid response from CryptoCompare")

        df = pd.DataFrame(data["Data"]["Data"])
        return df
    except Exception as e:
        print(f"❌ Помилка завантаження OHLCV: {e}")
        return None

async def analyze_crypto(symbol: str, timeframe: str = "4h"):
    df = fetch_ohlcv(symbol, timeframe)

    if df is None or df.empty:
        return None

    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["rsi"] = df["close"].pct_change().rolling(window=14).mean()
    df["sma"] = df["close"].rolling(window=20).mean()

    latest = df.iloc[-1]
    rsi = latest["rsi"]
    sma = latest["sma"]
    price = latest["close"]

    if pd.isna(rsi) or pd.isna(sma):
        return None

    if rsi < 30 and price > sma:
        signal = "🟢 LONG"
    elif rsi > 70 and price < sma:
        signal = "🔴 SHORT"
    else:
        signal = "⚪️ Очікування сигналу"

    entry_price = price
    exit_price = entry_price * 1.05 if signal == "🟢 LONG" else entry_price * 0.95

    indicators_str = f"{signal}"
    return indicators_str, entry_price, exit_price, rsi, sma