# services/market_data.py
import os
import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, SMAIndicator, MACD
from ta.volatility import BollingerBands

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

def fetch_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 50):
    url = f"https://min-api.cryptocompare.com/data/v2/histohour"
    params = {
        "fsym": symbol,
        "tsym": "USD",
        "limit": limit,
        "api_key": CRYPTOCOMPARE_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data["Response"] != "Success":
            return None
        df = pd.DataFrame(data["Data"]["Data"])
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df
    except Exception as e:
        print(f"❌ Помилка при завантаженні OHLCV: {e}")
        return None

def calculate_indicators(df: pd.DataFrame):
    close = df["close"]

    # RSI, SMA, EMA, MACD
    rsi = RSIIndicator(close).rsi().iloc[-1]
    sma = SMAIndicator(close).sma_indicator().iloc[-1]
    ema = EMAIndicator(close).ema_indicator().iloc[-1]
    macd_calc = MACD(close)
    macd = macd_calc.macd().iloc[-1]
    macd_signal = macd_calc.macd_signal().iloc[-1]

    # Bollinger Bands
    bb = BollingerBands(close)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]

    # Тренд
    recent_closes = close[-50:]
    trend = "висхідний" if recent_closes.iloc[-1] > recent_closes.iloc[0] else "низхідний"

    # Рівні підтримки/опору (приблизні)
    support = recent_closes.min()
    resistance = recent_closes.max()

    current_price = close.iloc[-1]
    entry_price = current_price
    exit_price = current_price  # Це зміниться після LLM

    indicators_str = (
        f"RSI: {rsi:.2f}, SMA: {sma:.2f}, EMA: {ema:.2f}, "
        f"MACD: {macd:.2f}, MACD Signal: {macd_signal:.2f}, "
        f"Bollinger Bands: [{bb_lower:.2f}, {bb_upper:.2f}], "
        f"Trend: {trend}, Support: {support:.2f}, Resistance: {resistance:.2f}"
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

async def analyze_crypto(symbol: str, timeframe: str):
    df = fetch_ohlcv(symbol, timeframe)
    if df is None or len(df) < 50:
        return None
    return calculate_indicators(df)