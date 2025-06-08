import requests

def get_crypto_prices(ids):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(ids), "vs_currencies": "usd"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {k: float(v["usd"]) for k, v in data.items()}
    except Exception as e:
        return {}