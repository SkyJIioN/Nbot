import requests
import pandas as pd
import numpy as np

CRYPTOCOMPARE_API_KEY = "ТВОЙ_API_KEY"
CRYPTOCOMPARE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"  # або histoday для 1D

def fetch_ohlcv(symbol: str, timeframe: str = "4h", limit: int = 100):
    # Перетворюємо timeframe у параметри для API
    tf_map = {"1h": 1, "4h": 4, "12h": 12}
    aggregate = tf_map.get(timeframe, 4)
    
    url = f"{CRYPTOCOMPARE_URL}?fsym={symbol.upper()}&tsym=USDT&limit={limit}&aggregate={aggregate}&api_key={CRYPTOCOMPARE_API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()["Data"]["Data"]
        if not data:
            raise ValueError("Empty OHLCV data")

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        print(f"❌ Помилка завантаження OHLCV: {e}")
        return None


def calculate_indicators(df: pd.DataFrame):
    df["sma"] = df["close"].rolling(window=14).mean()
    delta = df["close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))
    return df


def analyze_symbol(symbol: str, timeframe: str = "4h"):
    df = fetch_ohlcv(symbol, timeframe)
    if df is None:
        return None

    df = calculate_indicators(df)

    last_row = df.iloc[-1]
    price = last_row["close"]
    rsi = last_row["rsi"]
    sma = last_row["sma"]

    entry = "Нейтральна"
    if rsi < 30 and price > sma:
        entry = "LONG"
    elif rsi > 70 and price < sma:
        entry = "SHORT"

    entry_price = round(price, 2)
    exit_price = round(entry_price * 1.05 if entry == "LONG" else entry_price * 0.95, 2)

    indicators = (
        f"💹 RSI: {rsi:.2f}\n"
        f"📈 SMA: {sma:.2f}\n"
        f"💰 Поточна ціна: {price:.2f}"
    )

    return indicators_str, entry_price, exit_price, rsi, sma

# 🔁 Додано псевдонім:
analyze_crypto = analyze_symbol