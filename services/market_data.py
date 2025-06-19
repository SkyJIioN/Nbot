import os
import requests
import pandas as pd

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")  # встав у .env або напряму

def get_ohlcv(symbol: str, limit: int = 100):
    url = f"https://min-api.cryptocompare.com/data/v2/histohour"
    params = {
        "fsym": symbol.upper(),
        "tsym": "USDT",
        "limit": limit,
        "aggregate": 4  # 4-годинний інтервал
    }
    headers = {
        "authorization": f"Apikey {CRYPTOCOMPARE_API_KEY}"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if data["Response"] != "Success":
        raise Exception(f"CryptoCompare API error: {data.get('Message', 'Unknown error')}")

    df = pd.DataFrame(data["Data"]["Data"])
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

def analyze_symbol(symbol: str) -> str:
    try:
        df = get_ohlcv(symbol)
        df["sma"] = df["close"].rolling(window=10).mean()
        df["rsi"] = compute_rsi(df["close"])

        current_price = df["close"].iloc[-1]
        sma = df["sma"].iloc[-1]
        rsi = df["rsi"].iloc[-1]

        analysis = f"💰 Поточна ціна {symbol.upper()}: ${current_price:.2f}\n"
        analysis += f"📉 SMA(10): {sma:.2f}, RSI: {rsi:.2f}\n"

        if rsi < 30:
            analysis += "✅ Рекомендація: LONG (перепроданість)"
        elif rsi > 70:
            analysis += "⚠️ Рекомендація: SHORT (перекупленість)"
        else:
            analysis += "⏸️ Рекомендація: Очікування сигналу"

        return analysis

    except Exception as e:
        return f"❌ Помилка аналізу: {e}"

def compute_rsi(series, period: int = 14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi