import os
import requests
import pandas as pd

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

def get_ohlcv(symbol: str, timeframe: str):
    endpoint = "histohour" if timeframe == "1h" else "histoday"
    aggregate = 1 if timeframe == "1h" else (4 if timeframe == "4h" else 12)

    url = f"https://min-api.cryptocompare.com/data/v2/{endpoint}"
    params = {
        "fsym": symbol.upper(),
        "tsym": "USD",
        "limit": 100,
        "aggregate": aggregate,
        "api_key": CRYPTOCOMPARE_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("Response") != "Success" or not data["Data"]["Data"]:
            print(f"❌ API error: {data}")
            return None

        df = pd.DataFrame(data["Data"]["Data"])
        df = df[["time", "open", "high", "low", "close"]]
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    except Exception as e:
        print(f"❌ Exception while fetching OHLCV: {e}")
        return None


def calculate_indicators(df: pd.DataFrame):
    df["RSI"] = compute_rsi(df["close"])
    df["SMA"] = df["close"].rolling(window=14).mean()
    return df


def compute_rsi(series: pd.Series, period: int = 14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=period).mean()
    ma_down = down.rolling(window=period).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))


async def analyze_crypto(symbol: str, timeframe: str):
    df = get_ohlcv(symbol, timeframe)
    if df is None or df.empty:
        return None

    df = calculate_indicators(df)
    latest = df.iloc[-1]

    rsi = latest["RSI"]
    sma = latest["SMA"]
    close_price = latest["close"]

    # Проста стратегія
    if rsi < 30 and close_price > sma:
        recommendation = "🟢 LONG"
    elif rsi > 70 and close_price < sma:
        recommendation = "🔴 SHORT"
    else:
        recommendation = "⚪️ Очікування сигналу"

    indicators_str = (
        f"🔍 Індикатори:\n"
        f"• RSI: {rsi:.2f} ({'Надмірно продано' if rsi < 30 else 'Надмірно куплено' if rsi > 70 else 'Нейтрально'})\n"
        f"• SMA: {sma:.2f}\n"
        f"• Рекомендація: {recommendation}"
    )

    entry_price = close_price
    exit_price = sma if recommendation != "⚪️ Очікування сигналу" else None

    return indicators_str, entry_price, exit_price, rsi, sma