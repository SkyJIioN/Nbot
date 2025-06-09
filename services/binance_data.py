import requests

def get_crypto_prices():
    url = "https://api.binance.com/api/v3/ticker/price"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        result = {}
        for item in data:
            if item["symbol"] == "BTCUSDT":
                result["BTCUSDT"] = float(item["price"])
            elif item["symbol"] == "ETHUSDT":
                result["ETHUSDT"] = float(item["price"])
        return result
    except Exception as e:
        print(f"Binance error: {e}")
        return None