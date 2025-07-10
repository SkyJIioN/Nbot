import requests
import pandas as pd
import numpy as np
from datetime import datetime
from services.trend_lines import calculate_trend_lines
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.volatility import BollingerBands

API_KEY = "your_cryptocompare_api_key"


def fetch_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 50):
    url = f"https://min-api.cryptocompare.com/data/v2/histohour"
    params = {
        "fsym": symbol,
        "tsym": "USD",
        "limit": limit,
        "api_key": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'Data' not in data['Data']:
        raise ValueError("Помилка при завантаженні OHLCV: 'Data'")

    df = pd.DataFrame(data['Data']['Data'])
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df.set_index("time", inplace=True)
    return df


def calculate_indicators(df: pd.DataFrame):
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # Індикатори
    rsi = RSIIndicator(close).rsi().iloc[-1]
    sma = SMAIndicator(close, window=14).sma_indicator().iloc[-1]
    ema = EMAIndicator(close, window=14).ema_indicator().iloc[-1]

    macd = MACD(close)
    macd_val = macd.macd().iloc[-1]
    macd_signal = macd.macd_signal().iloc[-1]

    bb = BollingerBands(close)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]

    # Поточна ціна (остання)
    price = close.iloc[-1]
    entry_price = price
    exit_price = price

    # Тренд і рівні підтримки/опору
    trend, support, resistance = calculate_trend_lines(close)

    # Для текстового відображення
    indicators_str = f"RSI: {rsi:.2f}, SMA: {sma:.2f}, EMA: {ema:.2f}, MACD: {macd_val:.2f}/{macd_signal:.2f}"

    return (
        indicators_str,
        float(price),
        float(entry_price),
        float(exit_price),
        float(rsi),
        float(sma),
        float(ema),
        float(macd_val),
        float(macd_signal),
        float(bb_upper),
        float(bb_lower),
        trend,
        float(support),
        float(resistance),
        float(price)
    )


def analyze_crypto(symbol: str, timeframe: str):
    try:
        df = fetch_ohlcv(symbol, timeframe)
        return calculate_indicators(df)
    except Exception as e:
        print(f"❌ Помилка при аналізі {symbol}: {e}")
        return None