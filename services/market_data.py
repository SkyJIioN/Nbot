import requests

def get_crypto_prices():
    url = "https://api.binance.com/api/v3/ticker/price"
    symbols = {"BTCUSDT": "bitcoin", "ETHUSDT": "ethereum"}
    prices = {}

    for symbol, name in symbols.items():
        try:
            resp = requests.get(url, params={"symbol": symbol}, timeout=5)
            resp.raise_for_status()
            prices[name] = round(float(resp.json()["price"]), 2)
        except Exception as e:
            print(f"❌ Binance API помилка для {symbol}: {e}")
            prices[name] = "н/д"

    return prices