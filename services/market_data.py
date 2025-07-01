import requests
import pandas as pd
import numpy as np
from datetime import datetime

API_KEY = "ТВОЙ_CRYPTOCOMPARE_API_KEY"  # заміни на свій
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

def fetch_ohlcv(symbol: str, timeframe: str, limit: int = 100):
    url = BASE_URL
    params = {
        "fsym": symbol.upper(),
        "tsym": "USD",
        "limit": limit,
        "aggregate": 1,
        "api_key": API_KEY
    }

    if timeframe == "1h":
        params["aggregate"] = 1
    elif timeframe == "4h":
        params["aggregate"] = 4
    elif timeframe == "12h":
        params["aggregate"] = 12
    else:
        return None

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()["Data"]["Data"]

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        print(f"Помилка при завантаженні OHLCV: {e}")
        return None

def calculate_indicators(df: pd.DataFrame):
    if len(df) < 50:
        return None

    close = df["close"]
    current_price = close.iloc[-1]

    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    # SMA
    sma = close.rolling(window=20).mean()
    latest_sma = sma.iloc[-1]

    # EMA
    ema = close.ewm(span=20, adjust=False).mean()
    latest_ema = ema.iloc[-1]

    # MACD
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    latest_macd = macd.iloc[-1]
    latest_signal = signal.iloc[-1]

    # Bollinger Bands
    rolling_mean = close.rolling(window=20).mean()
    rolling_std = close.rolling(window=20).std()
    bb_upper = rolling_mean + (rolling_std * 2)
    bb_lower = rolling_mean - (rolling_std * 2)
    latest_bb_upper = bb_upper.iloc[-1]
    latest_bb_lower = bb_lower.iloc[-1]

    # Trend line (підтримка/опір)
    last_50 = close[-50:]
    support = min(last_50)
    resistance = max(last_50)
    trend = "Висхідний" if close.iloc[-1] > close.iloc[-50] else "Нисхідний"

    # Entry/Exit will be predicted by LLM

    indicators_str = (
        f"🔍 Індикатори:\n"
        f"• RSI: {latest_rsi:.2f}\n"
        f"• SMA: {latest_sma:.2f}\n"
        f"• EMA: {latest_ema:.2f}\n"
        f"• MACD: {latest_macd:.2f}\n"
        f"• MACD Signal: {latest_signal:.2f}\n"
        f"• Bollinger Bands: Верхня {latest_bb_upper:.2f}$ / Нижня {latest_bb_lower:.2f}$"
    )

    return (
    indicators_str,
    current_price,
    entry_price,
    exit_price,
    rsi,
    sma,
    ema,
    macd,
    macd_signal,
    bb_upper,
    bb_lower,
    trend,
    support,
    resistance
)

def analyze_crypto(symbol: str, timeframe: str):
    df = fetch_ohlcv(symbol, timeframe)
    if df is None:
        return None
    return calculate_indicators(df)