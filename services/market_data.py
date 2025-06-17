import requests
import os

COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")

headers = {
    "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY
}

def get_crypto_price(symbol: str) -> float | None:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params = {
        "symbol": symbol,
        "convert": "USD"
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    try:
        return data["data"][symbol]["quote"]["USD"]["price"]
    except KeyError:
        return None
