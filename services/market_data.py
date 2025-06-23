import requests
import pandas as pd
import numpy as np
from datetime import datetime

CRYPTOCOMPARE_API_KEY = "YOUR_API_KEY"  # 🔁 Замінити на твій ключ

BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"  # Для таймфреймів 1H, 4H, 12H


def fetch_ohlcv(symbol: str, timeframe: str, limit: int = 100):
    symbol = symbol.upper()
    aggregate = {"1h": 1, "4h": 4, "12h": 12}.get(timeframe, 4)

    url = f"{BASE_URL}?fsym={symbol}&tsym=USDT&limit={limit}&aggregate={aggregate}&api_key={CRYPTOCOMPARE_API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data["Response"] != "Success":
            print(f"⚠️ CryptoCompare error: {data.get('Message', 'No message')}")
            return None

        ohlcv = data["Data"]["Data"]
        df = pd.DataFrame(ohlcv)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)
        return df

    except Exception as e:
        print(f"❌ Помилка завантаження OHLCV: {e}")
        return None


def calculate_indicators(df: pd.DataFrame):
    if len(df) < 20:
        return None, None, None

    df["close"] = df["close"].astype(float)
    df["sma"] = df["close"].rolling(window=14).mean()
    delta = df["close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    latest = df.iloc[-1]
    return latest["close"], latest["sma"], latest["rsi"]


def generate_signal(price, sma, rsi):
    signal = "Очікування сигналу"

    if rsi is None or sma is None:
        return signal, price, price

    if rsi < 30 and price > sma:
        signal = "🔼 LONG сигнал"
        entry = price
        target = round(price * 1.02, 2)
    elif rsi > 70 and price < sma:
        signal = "🔽 SHORT сигнал"
        entry = price
        target = round(price * 0.98, 2)
    else:
        entry = price
        target = price

    return signal, entry, target


async def analyze_crypto(symbol: str, timeframe: str):
    df = fetch_ohlcv(symbol, timeframe)

    if df is None or len(df) < 20:
        return None

    price, sma, rsi = calculate_indicators(df)

    if price is None or sma is None or rsi is None:
        return None

    signal, entry_price, exit_price = generate_signal(price, sma, rsi)

    indicators = (
        f"🔍 Індикатори:\n"
        f"• RSI: {rsi:.2f} ({'Перепроданість' if rsi < 30 else 'Перекупленість' if rsi > 70 else 'Нейтрально'})\n"
        f"• SMA: {sma:.2f}\n"
        f"• Рекомендація: {signal}"
    )

    return indicators, entry_price, exit_price, rsi, sma, price