import requests
import pandas as pd
import numpy as np
from datetime import datetime

CRYPTOCOMPARE_API_KEY = "YOUR_API_KEY"
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

def get_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100):
    try:
        symbol = symbol.upper()
        aggregate = {"1h": 1, "4h": 4, "12h": 12}.get(timeframe, 1)
        url = f"{BASE_URL}?fsym={symbol}&tsym=USDT&limit={limit}&aggregate={aggregate}&api_key={CRYPTOCOMPARE_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data.get("Response") != "Success":
            print(f"❌ Error fetching OHLCV data: {data.get('Message')}")
            return None

        prices = data["Data"]["Data"]
        if not prices or len(prices) < 20:
            return None

        df = pd.DataFrame(prices)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)
        return df

    except Exception as e:
        print(f"❌ Error loading OHLCV data: {e}")
        return None

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    deltas = pd.Series(prices).diff().dropna()
    gains = deltas.where(deltas > 0, 0.0)
    losses = -deltas.where(deltas < 0, 0.0)

    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1] if not rsi.empty else None

def calculate_sma(prices, period=14):
    if len(prices) < period:
        return None
    return pd.Series(prices).rolling(window=period).mean().iloc[-1]

async def analyze_crypto(symbol: str, timeframe: str):
    df = get_ohlcv(symbol, timeframe)
    if df is None or df.empty:
        return None

    close = df["close"]
    if close.isnull().any():
        return None

    current_price = float(close.iloc[-1])
    rsi = calculate_rsi(close)
    sma = calculate_sma(close)

    if sma is None:
        return None

    # Визначаємо сигнал
    signal = "Очікування сигналу"
    if rsi is not None:
        if rsi > 70:
            signal = "🔴 Перекупленість — можливий Short"
        elif rsi < 30:
            signal = "🟢 Перепроданість — можливий Long"

    # Точки входу/виходу
    entry_price = current_price
    exit_price = current_price * 1.015 if rsi and rsi < 30 else current_price * 0.985

    # Форматування значень
    rsi_display = f"{rsi:.2f}" if rsi is not None and not np.isnan(rsi) else "Н/Д"
    sma_display = f"{sma:.2f}"
    indicators_str = (
        f"🔍 Індикатори:\n"
        f"• RSI: {rsi_display} ({signal if rsi_display != 'Н/Д' else 'Н/Д'})\n"
        f"• SMA: {sma_display}\n"
        f"• Рекомендація: {signal}"
    )

    return (
        indicators_str,
        round(entry_price, 2),
        round(exit_price, 2),
        rsi_display,
        sma_display,
        round(current_price, 2)
    )