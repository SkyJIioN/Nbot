# services/market_data.py

import requests
import pandas as pd

def get_binance_ohlcv(symbol: str, interval="4h", limit=100):
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol.upper() + "USDT",
            "interval": interval,
            "limit": limit
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        ohlcv = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        ohlcv["close"] = pd.to_numeric(ohlcv["close"])
        return ohlcv
    except Exception as e:
        print(f"Failed to fetch OHLCV data: {e}")
        return None

def calculate_indicators(df: pd.DataFrame):
    df["SMA_14"] = df["close"].rolling(window=14).mean()
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI_14"] = 100 - (100 / (1 + rs))
    return df

def analyze_symbol(symbol: str):
    df = get_binance_ohlcv(symbol)
    if df is None or df.empty:
        return None, f"Не вдалося отримати OHLCV дані з Binance для {symbol.upper()}"

    df = calculate_indicators(df)
    current_price = df["close"].iloc[-1]
    sma = df["SMA_14"].iloc[-1]
    rsi = df["RSI_14"].iloc[-1]

    prompt = (
        f"Поточна ціна {symbol.upper()} становить {current_price:.2f} USDT.\n"
        f"SMA(14): {sma:.2f}, RSI(14): {rsi:.2f}.\n"
        f"На основі цих технічних індикаторів, чи варто відкривати LONG чи SHORT позицію? "
        f"Дай коротку аналітику з точками входу і виходу українською мовою."
    )

    return prompt, None