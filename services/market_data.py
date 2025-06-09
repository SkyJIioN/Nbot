import requests
from config import BINANCE_BASE_URL

def get_crypto_prices():
    symbols = ["BTCUSDT", "ETHUSDT"]
    prices = {}
    for symbol in symbols:
        url = f"{BINANCE_BASE_URL}/api/v3/ticker/price?symbol={symbol}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            prices[symbol.lower()] = float(data['price'])
        except Exception as e:
            print(f"Error fetching {symbol} from Binance: {e}")
    return prices