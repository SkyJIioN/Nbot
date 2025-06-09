# services/market_data.py

import requests

def get_crypto_prices(tokens: list[str]) -> dict[str, float]:
    """
    Отримує поточні ціни криптовалют із Binance.
    :param tokens: Список ідентифікаторів монет (наприклад, ["bitcoin", "ethereum"])
    :return: Словник з цінами у форматі {"bitcoin": 10500.0, "ethereum": 2500.0}
    """
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        prices = {}
        for token in tokens:
            symbol = token.upper() + "USDT"
            match = next((item for item in data if item["symbol"] == symbol), None)
            if match:
                prices[token] = float(match["price"])
            else:
                prices[token] = None  # або "н/д"
        return prices
    except Exception as e:
        print(f"Error fetching Binance data: {e}")
        return {}