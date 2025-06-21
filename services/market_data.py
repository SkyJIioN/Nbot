import os
import httpx
import pandas as pd

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"

INTERVAL_MAPPING = {
    "1h": 1,
    "4h": 4,
    "12h": 12
}

async def fetch_ohlcv(symbol: str, timeframe: str):
    limit = 100
    aggregate = INTERVAL_MAPPING.get(timeframe, 1)

    url = (
        f"{BASE_URL}?fsym={symbol.upper()}&tsym=USDT"
        f"&limit={limit}&aggregate={aggregate}&api_key={CRYPTOCOMPARE_API_KEY}"
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("Response") != "Success":
                print(f"❌ CryptoCompare API error: {data.get('Message')}")
                return None

            return data["Data"]["Data"]
    except Exception as e:
        print(f"❌ Failed to fetch OHLCV data: {e}")
        return None

def calculate_indicators(df: pd.DataFrame):
    df["SMA"] = df["close"].rolling(window=14).mean()
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df

async def analyze_crypto(symbol: str, timeframe: str):
    ohlcv = await fetch_ohlcv(symbol, timeframe)

    if not ohlcv or len(ohlcv) < 20:
        return None

    df = pd.DataFrame(ohlcv)
    df = calculate_indicators(df)

    latest = df.iloc[-1]
    current_price = latest["close"]
    rsi = latest["RSI"]
    sma = latest["SMA"]

    if pd.isna(rsi) or pd.isna(sma):
        return None

    trend = "Очікування сигналу"
    if rsi < 30 and current_price > sma:
        trend = "🟢 LONG (купівля)"
    elif rsi > 70 and current_price < sma:
        trend = "🔴 SHORT (продаж)"

    entry_price = current_price
    exit_price = entry_price * (1.03 if "LONG" in trend else 0.97)

    indicators_str = "🔍 Індикатори:\n"
    indicators_str += f"• RSI: {rsi:.2f} ({'Перекупленість' if rsi > 70 else 'Перепроданість' if rsi < 30 else 'Нейтрально'})\n"
    indicators_str += f"• SMA: {sma:.2f}\n"
    indicators_str += f"• Рекомендація: {trend}"

    return indicators_str, entry_price, exit_price, rsi, sma