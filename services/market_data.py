import requests
import numpy as np
import os

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

HEADERS = {
    "authorization": f"Apikey {CRYPTOCOMPARE_API_KEY}"
}


def calculate_rsi(prices: list, period: int = 14):
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100. - 100. / (1. + rs)
    return rsi


def calculate_sma(prices: list, period: int = 14):
    if len(prices) < period:
        return sum(prices) / len(prices)
    return sum(prices[-period:]) / period


async def analyze_crypto(symbol: str, timeframe: str):
    symbol = symbol.upper()
    limit = 100
    aggregate = 1

    # Визначення інтервалу
    if timeframe == "1h":
        url = f"{BASE_URL}?fsym={symbol}&tsym=USDT&limit={limit}&aggregate={aggregate}"
    elif timeframe == "4h":
        url = f"{BASE_URL}?fsym={symbol}&tsym=USDT&limit={limit}&aggregate=4"
    elif timeframe == "12h":
        url = f"{BASE_URL}?fsym={symbol}&tsym=USDT&limit={limit}&aggregate=12"
    else:
        return None

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        if "Data" not in data or "Data" not in data["Data"]:
            return None

        ohlcv = data["Data"]["Data"]

        closes = [candle["close"] for candle in ohlcv if candle["close"] > 0]

        if len(closes) < 20:
            return None

        rsi = calculate_rsi(closes)
        sma = calculate_sma(closes)
        current_price = closes[-1]

        # Рекомендації
        if rsi > 70:
            recommendation = "🔴 Перекупленість (можлива корекція)"
        elif rsi < 30:
            recommendation = "🟢 Перепроданість (можливе зростання)"
        else:
            recommendation = "⚪️ Очікування сигналу"

        indicators_str = (
            f"🔍 Індикатори:\n"
            f"• RSI: {rsi:.2f} ({'Перекупленість' if rsi > 70 else 'Перепроданість' if rsi < 30 else 'Нейтрально'})\n"
            f"• SMA: {sma:.2f}\n"
            f"• Рекомендація: {recommendation}"
        )

        # Точки входу та виходу
        entry_price = current_price * 1.01
        exit_price = current_price * 0.97

        return indicators_str, entry_price, exit_price, rsi, sma, current_price

    except Exception as e:
        print(f"Помилка при завантаженні OHLCV: {e}")
        return None