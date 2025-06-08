import requests

def get_crypto_prices(symbols=["bitcoin", "ethereum"]):
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(symbols),
        "vs_currencies": "usd"
    }
    response = requests.get(url, params=params)
    data = response.json()

    prices = {}
    for symbol in symbols:
        price = data.get(symbol, {}).get("usd", "н/д")
        prices[symbol.upper()] = price

    return prices