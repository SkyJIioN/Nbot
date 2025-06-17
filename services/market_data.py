import os
import requests
import pandas as pd

COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")
BASE_URL = "https://pro-api.coinmarketcap.com"

HEADERS = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY,
}

def fetch_price_history(symbol: str) -> pd.DataFrame:
    url = f"{BASE_URL}/v1/cryptocurrency/ohlcv/historical"
    params = {
        "symbol": symbol,
        "convert": "USD",
        "interval": "4h",
        "count": 100
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        quotes = data["data"]["quotes"]
        df = pd.DataFrame([{
            "time": item["time_open"],
            "close": float(item["quote"]["USD"]["close"])
        } for item in quotes])
        return df
    except Exception as e:
        print(f"Error fetching historical data for {symbol}:", e)
        return pd.DataFrame()

def calculate_indicators(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}

    df["SMA_14"] = df["close"].rolling(window=14).mean()
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    RS = gain / loss
    df["RSI_14"] = 100 - (100 / (1 + RS))

    current_data = df.iloc[-1]
    return {
        "current_price": round(current_data["close"], 2),
        "SMA_14": round(current_data["SMA_14"], 2),
        "RSI_14": round(current_data["RSI_14"], 2),
    }

def get_indicators(symbol: str) -> dict:
    df = fetch_price_history(symbol)
    return calculate_indicators(df)