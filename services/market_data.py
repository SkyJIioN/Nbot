import requests
import pandas as pd 
import numpy as np from datetime 
import datetime

API_KEY = "YOUR_CRYPTOCOMPARE_API_KEY"

BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

HEADERS = { "authorization": f"Apikey {API_KEY}" }

def fetch_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100): url = f"{BASE_URL}?fsym={symbol.upper()}&tsym=USDT&limit={limit}" response = requests.get(url, headers=HEADERS)

if response.status_code != 200:
    print("Помилка при завантаженні OHLCV:", response.text)
    return None

data = response.json()["Data"]["Data"]
df = pd.DataFrame(data)
df["datetime"] = pd.to_datetime(df["time"], unit="s")
return df

def calculate_indicators(df): if df is None or df.empty: return None

df["close"] = df["close"]
df["rsi"] = compute_rsi(df["close"], 14)
df["sma"] = df["close"].rolling(window=14).mean()
df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
df["macd"] = df["close"].ewm(span=12, adjust=False).mean() - df["close"].ewm(span=26, adjust=False).mean()
df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

latest = df.iloc[-1]

recommendation = "Очікування сигналу"
if latest["macd"] > latest["macd_signal"] and latest["rsi"] < 70:
    recommendation = "🟢 LONG"
elif latest["macd"] < latest["macd_signal"] and latest["rsi"] > 30:
    recommendation = "🔴 SHORT"

indicators_str = (
    f"🔍 Індикатори:\n"
    f"• RSI: {latest['rsi']:.2f} ({interpret_rsi(latest['rsi'])})\n"
    f"• SMA: {latest['sma']:.2f}\n"
    f"• EMA(9): {latest['ema9']:.2f}\n"
    f"• EMA(21): {latest['ema21']:.2f}\n"
    f"• MACD: {latest['macd']:.2f}\n"
    f"• MACD Signal: {latest['macd_signal']:.2f}\n"
    f"• Рекомендація: {recommendation}"
)

return (
    indicators_str,
    latest["close"],
    latest["close"] * 1.02,
    latest["close"] * 0.98,
    latest["rsi"],
    latest["sma"]
)

def interpret_rsi(rsi): if rsi < 30: return "Перепроданість" elif rsi > 70: return "Перекупленість" return "Нейтрально"

def compute_rsi(series, period=14): delta = series.diff() gain = delta.where(delta > 0, 0.0) loss = -delta.where(delta < 0, 0.0)

avg_gain = gain.rolling(window=period).mean()
avg_loss = loss.rolling(window=period).mean()

rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
return rsi

def analyze_crypto(symbol: str, timeframe: str): df = fetch_ohlcv(symbol, timeframe) if df is None or len(df) < 30: return None return calculate_indicators(df)

