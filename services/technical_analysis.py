import pandas as pd

def calculate_indicators(df: pd.DataFrame) -> dict:
    df["SMA"] = df["close"].rolling(window=14).mean()
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    last_rsi = df["RSI"].iloc[-1]
    last_price = df["close"].iloc[-1]
    sma = df["SMA"].iloc[-1]

    signal = "Long" if last_rsi < 30 and last_price > sma else "Short" if last_rsi > 70 and last_price < sma else "Neutral"

    return {
        "RSI": round(last_rsi, 2),
        "SMA": round(sma, 2),
        "Price": round(last_price, 2),
        "Signal": signal
    }