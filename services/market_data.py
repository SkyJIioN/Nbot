import requests

def get_crypto_prices():
    try:
        symbols = {"bitcoin": "BTCUSDT", "ethereum": "ETHUSDT"}
        prices = {}

        for key, symbol in symbols.items():
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            prices[key] = float(data["price"])

        return prices
    except Exception as e:
        print(f"Error fetching Binance data: {e}")
        return {}