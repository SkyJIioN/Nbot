import requests
import pandas as pd
import numpy as np

def get_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100):
    url = "https://min-api.cryptocompare.com/data/v2/"
    aggregate_map = {
        "1h": ("histohour", 1),
        "4h": ("histohour", 4),
        "12h": ("histohour", 12),
    }

    if timeframe not in aggregate_map:
        raise ValueError("❌ Непідтримуваний таймфрейм")

    endpoint, agg = aggregate_map[timeframe]
    full_url = f"{url}{endpoint}?fsym={symbol.upper()}&tsym=USD&limit={limit}&aggregate={agg}"

    try:
        res = requests.get(full_url)
        data = res.json()
        candles = data["Data"]["Data"]

        if len(candles) < 50:
            print(f"⚠️ Недостатньо даних: {len(candles)} точок")
            return None

        df = pd.DataFrame(candles)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    except Exception as e:
        print(f"❌ Помилка при завантаженні OHLCV: {e}")
        return None


def calculate_indicators(df: pd.DataFrame):
    df["close"] = df["close"]

    df["RSI"] = compute_rsi(df["close"], 14)
    df["SMA"] = df["close"].rolling(window=14).mean()
    df["EMA"] = df["close"].ewm(span=14, adjust=False).mean()

    # MACD
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema_12 - ema_26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    return df


def compute_rsi(series, period: int = 14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def analyze_crypto(symbol: str, timeframe: str = "1h"):
    df = get_ohlcv(symbol, timeframe)
    if df is None:
        return None

    df = calculate_indicators(df)
    latest = df.iloc[-1]

    rsi = latest["RSI"]
    sma = latest["SMA"]
    ema = latest["EMA"]
    macd = latest["MACD"]
    macd_signal = latest["MACD_Signal"]
    price = latest["close"]

    recommendation = "⚪️ Очікування сигналу"
    if rsi and rsi < 30 and macd > macd_signal:
        recommendation = "🟢 LONG"
    elif rsi and rsi > 70 and macd < macd_signal:
        recommendation = "🔴 SHORT"

    entry_price = price
    exit_price = price * 1.02 if recommendation == "🟢 LONG" else price * 0.98 if recommendation == "🔴 SHORT" else price

    indicators_str = (
        f"🔍 Індикатори:\n"
        f"• RSI: {rsi:.2f} ({'Перепроданість' if rsi < 30 else 'Перекупленість' if rsi > 70 else 'Нейтрально'})\n"
        f"• SMA: {sma:.2f}\n"
        f"• EMA: {ema:.2f}\n"
        f"• MACD: {macd:.2f}\n"
        f"• MACD Signal: {macd_signal:.2f}\n"
        f"• Рекомендація: {recommendation}"
    )

    indicators_str, price, entry_price, exit_price, *_ = result