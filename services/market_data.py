import requests
import os

COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")

def fetch_market_data(symbol: str):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical"
    parameters = {
        "symbol": symbol,
        "convert": "USD",
        "time_period": "daily",
        "count": 7  # 7 днів, щоб приблизно відповідало 4h
    }
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY,
    }

    try:
        response = requests.get(url, headers=headers, params=parameters)
        response.raise_for_status()
        data = response.json()

        ohlcv_data = data["data"]["quotes"]
        formatted_data = ""
        for day in ohlcv_data:
            quote = day["quote"]["USD"]
            formatted_data += (
                f"Date: {day['time_open'][:10]}, "
                f"Open: {quote['open']}, High: {quote['high']}, "
                f"Low: {quote['low']}, Close: {quote['close']}, Volume: {quote['volume']}\n"
            )
        return formatted_data

    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None