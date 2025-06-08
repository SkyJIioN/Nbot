import requests
import logging

logger = logging.getLogger(__name__)

def get_crypto_prices(ids):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(ids), "vs_currencies": "usd"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(f"CoinGecko response: {data}")
        return {k: float(v["usd"]) for k, v in data.items() if "usd" in v}
    except Exception as e:
        logger.error(f"Error fetching CoinGecko data: {e}")
        return {}