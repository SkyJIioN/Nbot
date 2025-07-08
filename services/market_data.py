import os
import pandas as pd
from binance.client import Client
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, SMAIndicator, MACD
from ta.volatility import BollingerBands
from services.trend_lines import calculate_trend_info

# Ініціалізація Binance API
client = Client(api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_SECRET_KEY"))

def get_ohlcv_binance(symbol: str, interval: str = "1h", limit: int = 50) -> pd.DataFrame:
    pair = symbol.upper() + "USDT"
    klines = client.get_klines(symbol=pair, interval=interval, limit=limit)

    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])

    df["open"] = pd.to_numeric(df["open"])
    df["high"] = pd.to_numeric(df["high"])
    df["low"] = pd.to_numeric(df["low"])
    df["close"] = pd.to_numeric(df["close"])
    df["volume"] = pd.to_numeric(df["volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')

    return df[["timestamp", "open", "high", "low", "close", "volume"]]

def calculate_indicators(df: pd.DataFrame):
    if len(df) < 30:
        return None

    close = df["close"]

    rsi = RSIIndicator(close).rsi().iloc[-1]
    sma = SMAIndicator(close, window=20).sma_indicator().iloc[-1]
    ema = EMAIndicator(close, window=20).ema_indicator().iloc[-1]

    macd_obj = MACD(close)
    macd = macd_obj.macd().iloc[-1]
    macd_signal = macd_obj.macd_signal().iloc[-1]

    bb = BollingerBands(close)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]

    current_price = close.iloc[-1]
    entry_price = round(current_price, 5)
    exit_price = round(current_price, 5)

    trend, support, resistance = calculate_trend_info(df)

    indicators_str = f"RSI: {rsi:.2f}, SMA: {sma:.2f}, EMA: {ema:.2f}, MACD: {macd:.2f}, Bollinger: {bb_upper:.2f}/{bb_lower:.2f}"

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

def analyze_crypto(symbol: str, timeframe: str = "1h"):
    try:
        df = get_ohlcv_binance(symbol, interval=timeframe)
        return calculate_indicators(df)
    except Exception as e:
        print(f"❌ Помилка при завантаженні OHLCV Binance: {e}")
        return None