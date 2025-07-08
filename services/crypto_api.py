import requests

BINANCE_BASE_URL = "https://api.binance.com"

# Підтримувані таймфрейми Binance
SUPPORTED_INTERVALS = [
    "1m", "3m", "5m", "15m", "30m",
    "1h", "2h", "4h", "6h", "8h", "12h",
    "1d", "3d", "1w", "1M"
]

def get_ohlcv_data(symbol: str, interval: str = "1h", limit: int = 50):
    if interval not in SUPPORTED_INTERVALS:
        raise ValueError(f"⛔ Непідтримуваний таймфрейм: {interval}")

    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol.upper() + "USDT",
        "interval": interval,
        "limit": limit
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise Exception(f"❌ Помилка під час запиту до Binance API: {e}")

    # Перетворюємо відповіді в зручний формат
    ohlcv = []
    for candle in data:
        ohlcv.append({
            "timestamp": int(candle[0]),
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5])
        })

    return ohlcv