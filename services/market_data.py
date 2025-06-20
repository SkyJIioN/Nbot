import os
import requests
import pandas as pd

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

def get_ohlcv(symbol: str, timeframe: str, limit: int = 100):
    url = BASE_URL
    params = {
        "fsym": symbol.upper(),
        "tsym": "USDT",
        "limit": limit,
        "aggregate": timeframe_to_hours(timeframe),
        "api_key": CRYPTOCOMPARE_API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch OHLCV data: {response.status_code} {response.text}")

    data = response.json()["Data"]["Data"]
    if not data:
        raise Exception("No OHLCV data returned")

    df = pd.DataFrame(data)
    return df


def timeframe_to_hours(tf: str) -> int:
    return {
        "1h": 1,
        "4h": 4,
        "12h": 12
    }.get(tf.lower(), 4)


def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


def calculate_sma(prices: pd.Series, period: int = 20) -> float:
    return prices.rolling(window=period).mean().iloc[-1]


async def analyze_crypto(symbol: str, timeframe: str):
    try:
        df = get_ohlcv(symbol, timeframe)

        close_prices = df["close"]

        rsi = calculate_rsi(close_prices)
        sma = calculate_sma(close_prices)
        current_price = close_prices.iloc[-1]

        signal = ""
        if rsi < 30 and current_price > sma:
            signal = "🔼 Рекомендація: Відкрити LONG позицію"
        elif rsi > 70 and current_price < sma:
            signal = "🔽 Рекомендація: Відкрити SHORT позицію"
        else:
            signal = "⏳ Сигнал не сформовано, очікуємо кращої ситуації"

        entry_price = current_price
        exit_price = sma if signal != "⏳ Сигнал не сформовано, очікуємо кращої ситуації" else current_price

        indicators_str = f"{signal}\nЦіна: {current_price:.2f}$"

        return indicators_str, entry_price, exit_price, rsi, sma

    except Exception as e:
        print(f"❌ Error in analyze_crypto: {e}")
        return None