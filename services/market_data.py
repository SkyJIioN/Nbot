import pandas as pd
import numpy as np
import requests
from datetime import datetime
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import EMAIndicator, SMAIndicator, MACD, ADXIndicator
from ta.volatility import BollingerBands
from ta.volume import VWAP

API_KEY = "YOUR_CRYPTOCOMPARE_API_KEY"
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
        print(f"❌ Помилка при завантаженні OHLCV: {e}")
        return None

def calculate_indicators(df: pd.DataFrame):
    if len(df) < 50:
        return None

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volumefrom"]

    current_price = close.iloc[-1]

    rsi = RSIIndicator(close, window=14).rsi().iloc[-1]
    sma = SMAIndicator(close, window=20).sma_indicator().iloc[-1]
    ema = EMAIndicator(close, window=20).ema_indicator().iloc[-1]
    macd_indicator = MACD(close)
    macd = macd_indicator.macd().iloc[-1]
    macd_signal = macd_indicator.macd_signal().iloc[-1]
    
    bb = BollingerBands(close, window=20, window_dev=2)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]

    vwap = VWAP(high=high, low=low, close=close, volume=volume).vwap().iloc[-1]
    adx = ADXIndicator(high=high, low=low, close=close, window=14).adx().iloc[-1]
    stoch = StochasticOscillator(high=high, low=low, close=close, window=14, smooth_window=3)
    stoch_k = stoch.stoch().iloc[-1]
    stoch_d = stoch.stoch_signal().iloc[-1]

    # Трендові рівні (на основі останніх 50 свічок)
    support = low[-50:].min()
    resistance = high[-50:].max()
    trend = "висхідний" if close.iloc[-1] > close.iloc[-50] else "нисхідний"

    # Точки входу/виходу — поки прості, далі можна автоматизувати краще через LLM
    entry_price = current_price
    exit_price = current_price * 1.02 if rsi < 30 else current_price * 0.98 if rsi > 70 else current_price

    indicators_str = (
        f"🔍 Індикатори:\n"
        f"• RSI: {rsi:.2f}\n"
        f"• SMA: {sma:.2f}\n"
        f"• EMA: {ema:.2f}\n"
        f"• MACD: {macd:.2f} / {macd_signal:.2f}\n"
        f"• Bollinger Bands: верхня {bb_upper:.2f}, нижня {bb_lower:.2f}\n"
        f"• VWAP: {vwap:.2f}\n"
        f"• ADX: {adx:.2f}\n"
        f"• Stochastic RSI: K={stoch_k:.2f}, D={stoch_d:.2f}\n"
        f"• Тренд: {trend}\n"
        f"• Підтримка: {support:.2f} / Опір: {resistance:.2f}"
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