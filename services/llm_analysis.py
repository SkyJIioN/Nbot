import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, trend, support, resistance, price):
    return f"""
🔎 Аналіз криптовалюти {symbol} на таймфреймі {timeframe.upper()}.

📈 Технічні індикатори:
- Ціна: {price:.2f} USD
- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}
- MACD Signal: {macd_signal:.2f}
- Тренд: {trend}
- Лінія підтримки: {support:.2f}
- Лінія опору: {resistance:.2f}

🔍 Завдання:
Оціни ситуацію та надай короткий сигнал для трейдера.

📌 Формат відповіді:
- Позиція: LONG або SHORT
- Точка входу:
- Тейк-профіт:
- Стоп-лосс:
- Орієнтовний час:
- Опис ринкової ситуації (лаконічно українською)
"""


async def generate_signal_description(
    symbol: str,
    timeframe: str,
    rsi: float,
    sma: float,
    ema: float,
    macd: float,
    macd_signal: float,
    trend: str,
    support: float,
    resistance: float,
    price: float
) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "Ти професійний трейдер. Відповідай лаконічно українською мовою."
            },
            {
                "role": "user",
                "content": build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, trend, support, resistance, price)
            }
        ],
        "temperature": 0.4
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_URL, headers=headers, json=payload, timeout=15) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Помилка від Groq: {e}"