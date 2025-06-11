import os
import requests

COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")

def get_price(symbol: str) -> float:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY,
    }
    params = {
        "symbol": symbol.upper(),
        "convert": "USD",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        price = data["data"][symbol.upper()]["quote"]["USD"]["price"]
        print(f"[INFO] {symbol.upper()} price: {price}")
        return price

    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"[ERROR] Request failed: {req_err}")
    except KeyError:
        print(f"[ERROR] Unexpected response structure: {data}")
    except Exception as e:
        print(f"[ERROR] Unknown error: {e}")

    return 0.0  # повертає 0.0 при помилці