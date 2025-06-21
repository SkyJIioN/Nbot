import requests
import pandas as pd
import os

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

def calculate_rsi(prices: list, period: int = 14) -> float | None:
    if len(prices) < period + 1:
        return None

    df = pd.DataFrame(prices, columns=["close"])
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

def calculate_sma(prices: list, period: int = 14) -> float | None:
    if len(prices) < period:
        return None
    sma = pd.Series(prices).rolling(window=period).mean()
    return round(sma.iloc[-1], 2)

async def analyze_crypto(symbol: str, timeframe: str = "1h"):
    symbol = symbol.upper()
    aggregate_map = {
        "1h": 1,
        "4h": 4,
        "12h": 12
    }

    if timeframe not in aggregate_map:
        return None

    params = {
        "fsym": symbol,
        "tsym": "USD",
        "limit": 100,
        "aggregate": aggregate_map[timeframe],
        "api_key": CRYPTOCOMPARE_API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data["Response"] != "Success":
            return None

        prices = [candle["close"] for candle in data["Data"]["Data"] if candle["close"] > 0]

        if len(prices) < 20:
            return None

        rsi = calculate_rsi(prices)
        sma = calculate_sma(prices)
        current_price = prices[-1]

        if rsi is None or sma is None:
            return None

        # Рекомендація на основі RSI
        if rsi > 70:
            recommendation = "SHORT"
            entry_price = current_price * 1.01
            exit_price = sma * 0.99
        elif rsi < 30:
            recommendation = "LONG"
            entry_price = current_price * 0.99
            exit_price = sma * 1.01
        else:
            recommendation = "Очікування сигналу"
            entry_price = current_price
            exit_price = sma

        indicators_str = (
            f"🔍 Індикатори:\n"
            f"• RSI: {rsi:.2f} ({'Перекупленість' if rsi > 70 else 'Перепроданість' if rsi < 30 else 'Нейтрально'})\n"
            f"• SMA: {sma:.2f}\n"
            f"• Рекомендація: {recommendation}"
        )

        return indicators_str, entry_price, exit_price, rsi, sma, close 

    except Exception as e:
        print(f"❌ Помилка при завантаженні OHLCV: {e}")
        return None