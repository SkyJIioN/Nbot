import requests
import os

def get_crypto_prices(symbols):
    headers = {
        "X-CMC_PRO_API_KEY": os.getenv("COINMARKETCAP_API_KEY"),
    }
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    symbol_str = ",".join(symbols)
    try:
        response = requests.get(url, headers=headers, params={"symbol": symbol_str, "convert": "USD"})
        data = response.json()["data"]
        return {sym: data[sym]["quote"]["USD"]["price"] for sym in symbols}
    except Exception as e:
        print("CoinMarketCap error:", e)
        return {}