import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.volatility import BollingerBands
from services.crypto_api import get_ohlcv_data
from services.trend_lines import detect_trend_lines


def analyze_crypto(symbol: str, timeframe: str = "1h"):
    try:
        binance_symbol = symbol.upper() + "USDT"
        df = get_ohlcv_data(binance_symbol, timeframe)

        if df is None or df.empty:
            print(f"⚠️ Недостатньо даних для {symbol}")
            return None

        return calculate_indicators(df)

    except Exception as e:
        print(f"❌ Помилка при завантаженні OHLCV для {symbol}: {e}")
        return None


def calculate_indicators(df: pd.DataFrame):
    try:
        close = df["close"]

        rsi = RSIIndicator(close=close, window=14).rsi().iloc[-1]
        sma = SMAIndicator(close=close, window=14).sma_indicator().iloc[-1]
        ema = EMAIndicator(close=close, window=14).ema_indicator().iloc[-1]

        macd_indicator = MACD(close=close)
        macd = macd_indicator.macd().iloc[-1]
        macd_signal = macd_indicator.macd_signal().iloc[-1]

        bb = BollingerBands(close=close, window=20, window_dev=2)
        bb_upper = bb.bollinger_hband().iloc[-1]
        bb_lower = bb.bollinger_lband().iloc[-1]

        # Тренд і рівні
        trend, support, resistance = detect_trend_lines(df)

        # Поточна ціна = останній закритий бар
        current_price = float(close.iloc[-1])

        # Прості евристики для точок входу/виходу
        entry_price = round(current_price, 5)
        exit_price = round((support + resistance) / 2, 5)

        indicators_summary = (
            f"RSI: {rsi:.2f}, SMA: {sma:.2f}, EMA: {ema:.2f}, MACD: {macd:.2f}/{macd_signal:.2f}, "
            f"BB: {bb_lower:.2f}-{bb_upper:.2f}, Trend: {trend}"
        )

        return (
            indicators_summary,
            round(current_price, 5),
            entry_price,
            exit_price,
            round(rsi, 2),
            round(sma, 2),
            round(ema, 2),
            round(macd, 2),
            round(macd_signal, 2),
            round(bb_upper, 2),
            round(bb_lower, 2),
            trend,
            round(support, 2),
            round(resistance, 2),
        )

    except Exception as e:
        print(f"❌ Помилка при обрахунку індикаторів: {e}")
        return None