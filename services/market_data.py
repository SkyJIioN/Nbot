import requests
import os
import pandas as pd
from datetime import datetime

CMC_API_KEY = os.getenv("COINMARKETCAP_API_KEY")

def get_ohlcv_data(symbol: str):
    """Отримує OHLCV дані для заданого символу з CoinMarketCap."""
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical"
        params = {
            "symbol": symbol,
            "convert": "USD",
            "time_period": "daily",
            "count": 100,
        }
        headers = {
            "X-CMC_PRO_API_KEY": CMC_API_KEY,
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        quotes = data["data"]["quotes"]
        df = pd.DataFrame([{
            "time": datetime.strptime(q["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            "open": q["quote"]["USD"]["open"],
            "high": q["quote"]["USD"]["high"],
            "low": q["quote"]["USD"]["low"],
            "close": q["quote"]["USD"]["close"],
            "volume": q["quote"]["USD"]["volume"]
        } for q in quotes])

        return df

    except Exception as e:
        print("Error fetching OHLCV:", e)
        return None