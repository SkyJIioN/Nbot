import requests
import pandas as pd

def fetch_historical_prices(symbol: str, api_key: str) -> pd.DataFrame:
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical"
    headers = {"X-CMC_PRO_API_KEY": api_key}
    params = {"symbol": symbol.upper(), "convert": "USD", "interval": "daily", "count": 100}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()["data"]["quotes"]

    df = pd.DataFrame({
        "timestamp": [d["timestamp"] for d in data],
        "close": [d["quote"]["USD"]["close"] for d in data],
    })
    df["close"] = df["close"].astype(float)
    return df

def analyze_technical(df: pd.DataFrame) -> dict:
    df["SMA"] = df["close"].rolling(window=14).mean()
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    latest = df.iloc[-1]
    recommendation = "Нейтрально"
    if latest["close"] > latest["SMA"] and latest["RSI"] < 70:
        recommendation = "LONG"
    elif latest["close"] < latest["SMA"] and latest["RSI"] > 30:
        recommendation = "SHORT"

    return {
        "price": round(latest["close"], 2),
        "SMA": round(latest["SMA"], 2),
        "RSI": round(latest["RSI"], 2),
        "recommendation": recommendation
    }