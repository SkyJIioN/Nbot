import os
import requests

CMC_API_KEY = os.getenv("COINMARKETCAP_API_KEY")


def get_price(symbol: str) -> float:
    symbol_map = {"bitcoin": "BTC", "ethereum": "ETH"}
    cmc_symbol = symbol_map.get(symbol.lower())

    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"symbol": cmc_symbol}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return round(data["data"][cmc_symbol]["quote"]["USD"]["price"], 2)
