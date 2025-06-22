import requests
import numpy as np
import os

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")

BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

def fetch_ohlcv(symbol: str, timeframe: str):
    symbol = symbol.upper()
    mapping = {"1h": 60, "4h": 240, "12h": 720}
    limit = 100

    if timeframe not in mapping:
        raise ValueError("❌ Непідтримуваний таймфрейм")

    aggregate = mapping[timeframe] // 60

    url = f"{BASE_URL}?fsym={symbol}&tsym=USDT&limit={limit}&aggregate={aggregate}"
    headers = {"authorization": f"Apikey {CRYPTOCOMPARE_API_KEY}"}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if "Data" not in data or "Data" not in data["Data"]:
            print(f"❌ Помилка завантаження OHLCV: {data}")
            return None

        return data["Data"]["Data"]
    except Exception as e:
        print(f"❌ Помилка при запиті: {e}")
        return None

def calculate_rsi(closes, period=14):
    deltas = np.diff(closes)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period if seed[seed < 0].size > 0 else 0.001
    rs = up / down
    rsi = [100.0 - (100.0 / (1.0 + rs))]

    for delta in deltas[period:]:
        up_val = max(delta, 0)
        down_val = -min(delta, 0)
        up = (up * (period - 1) + up_val) / period
        down = (down * (period - 1) + down_val) / period
        rs = up / down if down != 0 else 0
        rsi.append(100.0 - (100.0 / (1.0 + rs)))
    return rsi[-1]

def calculate_sma(closes, period=20):
    if len(closes) < period:
        return None
    return np.mean(closes[-period:])

def get_current_price(symbol: str):
    url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol.upper()}&tsyms=USDT"
    headers = {"authorization": f"Apikey {CRYPTOCOMPARE_API_KEY}"}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get("USDT")
    except Exception as e:
        print(f"❌ Помилка отримання поточної ціни: {e}")
        return None

async def analyze_crypto(symbol: str, timeframe: str):
    ohlcv = fetch_ohlcv(symbol, timeframe)
    if not ohlcv or len(ohlcv) < 30:
        return None

    closes = [candle["close"] for candle in ohlcv]

    rsi = calculate_rsi(closes)
    sma = calculate_sma(closes)

    if sma is None:
        return None

    current_price = closes[-1]

    # Сигнали
    if rsi > 70:
        signal = "🔴 Перекупленість"
        recommendation = "Short"
    elif rsi < 30:
        signal = "🟢 Перепроданість"
        recommendation = "Long"
    else:
        signal = "⚪️ Очікування сигналу"
        recommendation = "Очікування"

    # Рекомендовані точки
    if recommendation == "Long":
        entry_price = current_price * 0.99
        exit_price = current_price * 1.03
    elif recommendation == "Short":
        entry_price = current_price * 1.01
        exit_price = current_price * 0.97
    else:
        entry_price = current_price
        exit_price = current_price

    indicators_str = (
        f"🔍 Індикатори:\n"
        f"• RSI: {rsi:.2f} ({'Перепроданість' if rsi < 30 else 'Перекупленість' if rsi > 70 else 'Нейтрально'})\n"
        f"• SMA: {sma:.2f}\n"
        f"• Рекомендація: {signal}"
    )

    return indicators_str, entry_price, exit_price, rsi, sma
