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

def calculate_trendlines(df: pd.DataFrame):
    closes = df["close"][-50:]
    minima = closes[(closes.shift(1) > closes) & (closes.shift(-1) > closes)]
    maxima = closes[(closes.shift(1) < closes) & (closes.shift(-1) < closes)]

    support = minima.min() if not minima.empty else closes.min()
    resistance = maxima.max() if not maxima.empty else closes.max()

    trend = "висхідний" if closes.iloc[-1] > closes.iloc[0] else "низхідний" if closes.iloc[-1] < closes.iloc[0] else "флет"

    return trend, support, resistance

def calculate_indicators(df: pd.DataFrame):
    if len(df) < 50:
        return None

    close = df["close"]
    current_price = close.iloc[-1]

    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    sma = close.rolling(window=20).mean()
    latest_sma = sma.iloc[-1]

    ema = close.ewm(span=20, adjust=False).mean()
    latest_ema = ema.iloc[-1]

    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    latest_macd = macd.iloc[-1]
    latest_signal = signal.iloc[-1]

    std = close.rolling(window=20).std()
    bb_upper = latest_sma + (2 * std.iloc[-1])
    bb_lower = latest_sma - (2 * std.iloc[-1])

    signal_text = (
        "🟢 Можливий LONG" if latest_rsi < 30 and current_price > latest_ema
        else "🔴 Можливий SHORT" if latest_rsi > 70 and current_price < latest_ema
        else "⚪️ Очікування сигналу"
    )

    indicators_str = (
        f"🔍 Індикатори:\n"
        f"• RSI: {latest_rsi:.2f} ({'Перепроданість' if latest_rsi < 30 else 'Перекупленість' if latest_rsi > 70 else 'Нейтрально'})\n"
        f"• SMA: {latest_sma:.2f}\n"
        f"• EMA: {latest_ema:.2f}\n"
        f"• MACD: {latest_macd:.2f}\n"
        f"• MACD Signal: {latest_signal:.2f}\n"
        f"• Bollinger Bands: Верхня {bb_upper:.2f} / Нижня {bb_lower:.2f}\n"
        f"• Рекомендація: {signal_text}"
    )

    entry_price = current_price
    exit_price = (
        current_price * 1.02 if signal_text == "🟢 Можливий LONG"
        else current_price * 0.98 if signal_text == "🔴 Можливий SHORT"
        else current_price
    )

    trend, support, resistance = calculate_trendlines(df)

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
        trend,
        support,
        resistance
    )

def analyze_crypto(symbol: str, timeframe: str):
    df = fetch_ohlcv(symbol, timeframe)
    if df is None:
        return None
    return calculate_indicators(df)