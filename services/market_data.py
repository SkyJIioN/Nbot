import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.volatility import BollingerBands
from services.trend_lines import calculate_trend_info
from services.crypto_api import get_ohlcv_data


def calculate_indicators(df: pd.DataFrame):
    close = df['close']

    # RSI
    rsi = RSIIndicator(close=close, window=14).rsi().iloc[-1]

    # SMA
    sma = SMAIndicator(close=close, window=20).sma_indicator().iloc[-1]

    # EMA
    ema = EMAIndicator(close=close, window=20).ema_indicator().iloc[-1]

    # MACD
    macd_indicator = MACD(close=close)
    macd = macd_indicator.macd().iloc[-1]
    macd_signal = macd_indicator.macd_signal().iloc[-1]

    # Bollinger Bands
    bb_indicator = BollingerBands(close=close, window=20, window_dev=2)
    bb_upper = bb_indicator.bollinger_hband().iloc[-1]
    bb_lower = bb_indicator.bollinger_lband().iloc[-1]

    # Поточна ціна
    current_price = close.iloc[-1]

    # Прості логіки для точки входу/виходу
    entry_price = current_price
    exit_price = current_price

    # Тренд і лінії підтримки/опору
    trend, support, resistance = calculate_trend_info(df[-50:])

    indicators_str = f"RSI: {rsi:.2f}, SMA: {sma:.2f}, EMA: {ema:.2f}, MACD: {macd:.2f}/{macd_signal:.2f}"

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
    try:
        df = get_ohlcv_data(symbol, timeframe)
        if df is None or len(df) < 50:
            return None
        return calculate_indicators(df)
    except Exception as e:
        print(f"❌ Помилка при завантаженні OHLCV: {e}")
df = get_ohlcv_data(symbol, timeframe)
if df is None or df.empty:
    print(f"⚠️ Помилка: Порожній DataFrame для {symbol}")
    return None
        return None