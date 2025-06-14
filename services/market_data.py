import os
import requests

CMC_API_KEY = os.getenv("CMC_API_KEY")

def fetch_price(symbol: str) -> float | None:
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"symbol": symbol, "convert": "USD"}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data["data"][symbol]["quote"]["USD"]["price"]
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None