import os
import requests

CMC_API_KEY = os.getenv("CMC_API_KEY")

async def get_price(symbol: str):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"symbol": symbol, "convert": "USD"}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return round(data["data"][symbol]["quote"]["USD"]["price"], 2)
    except Exception as e:
        print(f"Error fetching {symbol} from CoinMarketCap: {e}")
        return None
