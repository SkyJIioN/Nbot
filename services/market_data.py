import requests
import pandas as pd
import numpy as np

CRYPTOCOMPARE_API_KEY = "YOUR_CRYPTOCOMPARE_API_KEY"
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

def get_ohlcv(symbol: str, timeframe: str):
    limit_map = {"1h": 100, "4h": 100, "12h": 100}
    aggregate_map = {"1h": 1, "4h": 4, "12h": 12}

    if timeframe not in limit_map:
        raise ValueError("Невідомий таймфрейм")

    params = {
        "fsym": symbol.upper(),
        "tsym": "USD",
        "limit": limit_map[timeframe],
        "aggregate": aggregate_map[timeframe],
        "api_key": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if data["Response"] != "Success":
        raise ValueError(f"Помилка при завантаженні OHLCV: {data.get('Message', 'Unknown error')}")

    df = pd.DataFrame(data["Data"]["Data"])
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

def calculate_indicators(df):
    df["SMA"] = df["close"].rolling(window=14).mean()
    df["EMA"] = df["close"].ewm(span=14, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    return df

def generate_recommendation(df):
    latest = df.iloc[-1]
    price = latest["close"]
    sma = latest["SMA"]
    ema = latest["EMA"]
    rsi = latest["RSI"]
    macd = latest["MACD"]
    signal = latest["Signal"]

    rsi_state = "Нейтрально"
    if rsi > 70:
        rsi_state = "Перекупленість"
    elif rsi < 30:
        rsi_state = "Перепроданість"

    # Рекомендація
    if macd > signal and rsi < 70 and price > ema:
        recommendation = "🟢 LONG"
    elif macd < signal and rsi > 30 and price < ema:
        recommendation = "🔴 SHORT"
    else:
        recommendation = "⚪️ Очікування сигналу"

    return rsi_state, price, sma, ema, rsi, macd, signal, recommendation

async def analyze_crypto(symbol: str, timeframe: str):
    try:
        df = get_ohlcv(symbol, timeframe)
        df = calculate_indicators(df)

        if df.isnull().values.any():
            return None

        rsi_state, price, sma, ema, rsi, macd, signal, recommendation = generate_recommendation(df)

        indicators_str = (
            f"🔍 Індикатори:\n"
            f"• RSI: {rsi:.2f} ({rsi_state})\n"
            f"• SMA: {sma:.2f}\n"
            f"• EMA: {ema:.2f}\n"
            f"• MACD: {macd:.2f}\n"
            f"• Signal Line: {signal:.2f}\n"
            f"• Рекомендація: {recommendation}"
        )

        entry_price = price
        exit_price = price * 1.01 if recommendation == "🟢 LONG" else price * 0.99

        return indicators_str, price, entry_price, exit_price, rsi, sma

    except Exception as e:
        print(f"❌ Помилка при аналізі: {e}")
        return None