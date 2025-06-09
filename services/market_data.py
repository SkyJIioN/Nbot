import requests
import logging

logger = logging.getLogger(__name__)

def get_crypto_prices():
    try:
        btc_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        eth_url = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"

        btc_response = requests.get(btc_url)
        eth_response = requests.get(eth_url)

        btc_price = float(btc_response.json()["price"])
        eth_price = float(eth_response.json()["price"])

        return {
            "bitcoin": round(btc_price, 2),
            "ethereum": round(eth_price, 2)
        }

    except Exception as e:
        logger.error(f"Binance API error: {e}")
        return None