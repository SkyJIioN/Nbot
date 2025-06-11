import requests
import pandas as pd
from datetime import datetime
import os

CMC_API_KEY = os.getenv("CMC_API_KEY")

def get_historical_prices(symbol: str):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical"
    params = {
        "symbol": symbol.upper(),
        "convert": "USD",
        "time_period": "daily",
        "time_start": (datetime.now().date()).isoformat(),  # сьогодні
        "count": 1
    }
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if "data" not in data or "quotes" not in data["data"]:
        raise Exception("Invalid historical data response")

    quotes = data["data"]["quotes"]
    df = pd.DataFrame(quotes)
    df["time_open"] = pd.to_datetime(df["time_open"])
    return df