import requests
import pandas as pd


def fetch_binance_ohlcv(symbol: str, interval: str = "4h", limit: int = 100):
    """Отримує OHLCV дані з Binance"""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}USDT&interval={interval}&limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    ohlcv = [
        {
            "open_time": entry[0],
            "open": float(entry[1]),
            "high": float(entry[2]),
            "low": float(entry[3]),
            "close": float(entry[4]),
            "volume": float(entry[5]),
        }
        for entry in data
    ]
    return pd.DataFrame(ohlcv)


def analyze_symbol(symbol: str) -> str:
    """Аналізує валюту за RSI та SMA (4H)"""
    try:
        df = fetch_binance_ohlcv(symbol)
    except Exception as e:
        return f"❌ Не вдалося отримати дані для {symbol.upper()}: {e}"

    # Обчислення SMA (14)
    df["sma"] = df["close"].rolling(window=14).mean()

    # Обчислення RSI (14)
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # Поточні значення
    current_price = df["close"].iloc[-1]
    sma = df["sma"].iloc[-1]
    rsi = df["rsi"].iloc[-1]

    # Формування результату
    analysis = f"📊 Аналіз {symbol.upper()} (4H):\n"
    analysis += f"Ціна: ${current_price:.2f}\n"
    analysis += f"SMA(14): ${sma:.2f}\n"
    analysis += f"RSI(14): {rsi:.2f}\n\n"

    # Проста стратегія на основі RSI та SMA
    if rsi < 40 and current_price > sma:
        analysis += "✅ Рекомендація: LONG (перепроданість + ціна вище середнього)"
    elif rsi > 60 and current_price < sma:
        analysis += "⚠️ Рекомендація: SHORT (перекупленість + ціна нижче середнього)"
    else:
        analysis += "⏸️ Очікування: немає чіткого сигналу"

    return analysis