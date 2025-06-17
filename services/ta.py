import pandas as pd

def calculate_indicators(df: pd.DataFrame) -> dict:
    """
    Розрахунок RSI та SMA на основі OHLCV даних.
    Повертає останні значення індикаторів.
    """
    indicators = {}

    # SMA (Simple Moving Average)
    df["SMA_14"] = df["close"].rolling(window=14).mean()
    indicators["SMA_14"] = round(df["SMA_14"].iloc[-1], 2)

    # RSI (Relative Strength Index)
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI_14"] = 100 - (100 / (1 + rs))
    indicators["RSI_14"] = round(df["RSI_14"].iloc[-1], 2)

    # Поточна ціна
    indicators["current_price"] = round(df["close"].iloc[-1], 2)

    return indicators