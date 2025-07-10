import aiohttp
import os
import pandas as pd
from datetime import datetime

BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

def format_symbol(symbol: str) -> str:
    """Повертає символ у форматі Binance (наприклад, BTC -> BTCUSDT)."""
    return symbol.upper() + "USDT"

def convert_binance_interval(interval: str) -> str:
    """Переводить таймфрейм у формат Binance."""
    valid = {"15m", "1h", "4h", "12h", "1d"}
    return interval if interval in valid else "1h"

async def get_ohlcv_data(symbol: str, interval: str = "1h", limit: int = 50):
    binance_symbol = format_symbol(symbol)
    interval = convert_binance_interval(interval)

    params = {
        "symbol": binance_symbol,
        "interval": interval,
        "limit": limit
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BINANCE_API_URL, params=params) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"❌ Помилка під час запиту до Binance API: {resp.status} {text}")
                    return None

                data = await resp.json()

                if not isinstance(data, list) or not data:
                    print(f"❌ Невірний формат відповіді від Binance API: {data}")
                    return None

                # Формуємо DataFrame
                df = pd.DataFrame(data, columns=[
                    "timestamp", "open", "high", "low", "close", "volume",
                    "_", "_", "_", "_", "_", "_"
                ])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                df.set_index("timestamp", inplace=True)

                for col in ["open", "high", "low", "close", "volume"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

                print(f"📥 Binance OHLCV {symbol}: {len(df)} рядків")
                return df

    except Exception as e:
        print(f"❌ Помилка при отриманні OHLCV для {symbol}: {e}")
        return None