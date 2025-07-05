import os
import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.volatility import BollingerBands
from datetime import datetime

API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"


def fetch_ohlcv(symbol: str, limit: int = 50):
    params = {
        "fsym": symbol,
        "tsym": "USD",
        "limit": limit,
        "api_key": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        if "Data" in data and "Data" in data["Data"]:
            candles = data["Data"]["Data"]
            df = pd.DataFrame(candles)
            df["timestamp"] = pd.to_datetime(df["time"], unit="s")
            return df
        return None
    except Exception as e:
        print(f"❌ Помилка при завантаженні OHLCV: {e}")
        return None


def calculate_indicators(df: pd.DataFrame):
    if df is None or df.empty:
        return None

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volumefrom"]

    rsi = RSIIndicator(close).rsi().iloc[-1]
    sma = SMAIndicator(close, window=14).sma_indicator().iloc[-1]
    ema = EMAIndicator(close, window=14).ema_indicator().iloc[-1]

    macd_indicator = MACD(close)
    macd = macd_indicator.macd().iloc[-1]
    macd_signal = macd_indicator.macd_signal().iloc[-1]

    bb = BollingerBands(close)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]

    adx = ADXIndicator(high=high, low=low, close=close).adx().iloc[-1]

    stoch = StochasticOscillator(high=high, low=low, close=close)
    stoch_rsi = stoch.stoch().iloc[-1]

    # Тренд: підтримка/опір
    support = df['low'].iloc[-50:].min()
    resistance = df['high'].iloc[-50:].max()
    trend = "висхідний" if close.iloc[-1] > sma else "нисхідний"

    # Точка входу/виходу - Placeholder (поки просто поточна ціна)
    entry_price = close.iloc[-1]
    exit_price = close.iloc[-1]

    indicators_str = f"RSI: {rsi:.2f}, SMA: {sma:.2f}, EMA: {ema:.2f}, MACD: {macd:.2f}, Signal: {macd_signal:.2f}"

    return (
        indicators_str,
        close.iloc[-1],  # current_price
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


def analyze_crypto(symbol: str, timeframe: str = "1h"):
    df = fetch_ohlcv(symbol)
    if df is not None:
        return calculate_indicators(df)
    return None
