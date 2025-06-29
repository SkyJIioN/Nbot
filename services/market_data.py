import requests
import pandas as pd
import numpy as np
from datetime import datetime

API_KEY = "ТВОЙ_CRYPTOCOMPARE_API_KEY"  # Заміни на свій ключ
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

def fetch_ohlcv(symbol: str, timeframe: str, limit: int = 100):
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
        response = requests.get(BASE_URL, params=params)
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
    if df is None or len(df) < 50:
        return None

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volumeto"]
    current_price = close.iloc[-1]

    # RSI
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
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
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    latest_macd = macd.iloc[-1]
    latest_signal = signal.iloc[-1]

    # Bollinger Bands
    std = close.rolling(window=20).std()
    bb_upper = latest_sma + (2 * std.iloc[-1])
    bb_lower = latest_sma - (2 * std.iloc[-1])

    # VWAP
    typical_price = (high + low + close) / 3
    cumulative_vp = (typical_price * volume).cumsum()
    cumulative_volume = volume.cumsum()
    vwap = (cumulative_vp / cumulative_volume).iloc[-1]

    # Рекомендація
    if latest_rsi < 30 and current_price > latest_ema:
        signal_text = "🟢 Можливий LONG"
    elif latest_rsi > 70 and current_price < latest_ema:
        signal_text = "🔴 Можливий SHORT"
    else:
        signal_text = "⚪️ Очікування сигналу"

    indicators_str = (
        f"🔍 Індикатори:\n"
        f"• RSI: {latest_rsi:.2f} ({'Перепроданість' if latest_rsi < 30 else 'Перекупленість' if latest_rsi > 70 else 'Нейтрально'})\n"
        f"• SMA: {latest_sma:.2f}\n"
        f"• EMA: {latest_ema:.2f}\n"
        f"• MACD: {latest_macd:.2f}, Сигнальна: {latest_signal:.2f}\n"
        f"• Bollinger Bands: Верхня {bb_upper:.2f}, Нижня {bb_lower:.2f}\n"
        f"• VWAP: {vwap:.2f}\n"
        f"• Рекомендація: {signal_text}"
    )

    entry_price = current_price
    exit_price = (
        current_price * 1.02 if signal_text == "🟢 Можливий LONG"
        else current_price * 0.98 if signal_text == "🔴 Можливий SHORT"
        else current_price
    )

    return (
        indicators_str,
        current_price,
        entry_price,
        exit_price,
        latest_rsi,
        latest_sma,
        latest_ema,
        latest_macd,
        latest_signal,
        bb_upper,
        bb_lower,
        vwap
    )

def analyze_crypto(symbol: str, timeframe: str):
    df = fetch_ohlcv(symbol, timeframe)
    if df is None:
        return None
    return calculate_indicators(df)