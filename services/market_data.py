import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

def get_ohlcv(symbol: str, limit: int = 50):
    url = f"https://min-api.cryptocompare.com/data/v2/histohour"
    params = {
        "fsym": symbol,
        "tsym": "USDT",
        "limit": limit,
        "aggregate": 4,  # 4 години
        "api_key": CRYPTOCOMPARE_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data["Response"] != "Success":
            raise ValueError(f"CryptoCompare API Error: {data.get('Message', 'No message')}")
        df = pd.DataFrame(data["Data"]["Data"])
        return df
    except Exception as e:
        print(f"Failed to fetch OHLCV data for {symbol}: {e}")
        return None

def calculate_indicators(df: pd.DataFrame):
    df["SMA"] = df["close"].rolling(window=5).mean()
    df["EMA"] = df["close"].ewm(span=5, adjust=False).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

def analyze_symbol(symbol: str) -> str:
    df = get_ohlcv(symbol)
    if df is None or df.empty:
        return f"⚠️ Не вдалося отримати дані для {symbol}."

    df = calculate_indicators(df)
    last = df.iloc[-1]
    close_price = last["close"]
    sma = last["SMA"]
    rsi = last["RSI"]

    message = (
        f"📊 Аналіз {symbol}/USDT (4H):\n"
        f"Ціна: ${close_price:.2f}\n"
        f"RSI: {rsi:.2f}\n"
        f"SMA: {sma:.2f}\n"
    )

    signal = "⏳ Сигнал: Очікування чіткого сигналу."
    entry = ""
    exit_ = ""

    if rsi < 30:
        signal = "🔽 Сигнал: Перепроданість. Можливий LONG."
        entry_price = close_price * 0.99
        exit_price = close_price * 1.03
        entry = f"🔹 Рекомендована точка входу: ${entry_price:.2f}\n"
        exit_ = f"🔸 Рекомендована точка виходу: ${exit_price:.2f}\n"

    elif rsi > 70:
        signal = "🔼 Сигнал: Перекупленість. Можливий SHORT."
        entry_price = close_price * 1.01
        exit_price = close_price * 0.97
        entry = f"🔹 Рекомендована точка входу: ${entry_price:.2f}\n"
        exit_ = f"🔸 Рекомендована точка виходу: ${exit_price:.2f}\n"

    message += f"{signal}\n{entry}{exit_}"
    return message