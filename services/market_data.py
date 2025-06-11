# services/market_data.py

import requests
import os

CMC_API_KEY = os.getenv("CMC_API_KEY")

def get_price(symbol: str) -> float:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "X-CMC_PRO_API_KEY": CMC_API_KEY
    }
    params = {
        "symbol": symbol.upper(),
        "convert": "USD"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    try:
        price = data["data"][symbol.upper()]["quote"]["USD"]["price"]
        return price
    except KeyError:
        raise ValueError(f"Не вдалося отримати ціну для {symbol}")