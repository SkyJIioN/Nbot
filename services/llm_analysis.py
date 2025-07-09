# services/llm_analysis.py
import os
import aiohttp

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-70b-8192"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance, price):
    return (
        f"Виконай технічний аналіз для {symbol} на таймфреймі {timeframe.upper()}.\n"
        f"Ось ринкові дані:\n"
        f"- Поточна ціна: {price:.5f}$\n"
        f"- RSI: {rsi:.2f}\n"
        f"- SMA: {sma:.2f}\n"
        f"- EMA: {ema:.2f}\n"
        f"- MACD: {macd:.2f}, Сигнальна: {macd_signal:.2f}\n"
        f"- Bollinger Bands: Верхня {bb_upper:.2f}$ / Нижня {bb_lower:.2f}$\n"
        f"- Тренд: {trend.capitalize()}\n"
        f"- Лінія підтримки: {support:.2f}$\n"
        f"- Лінія опору: {resistance:.2f}$\n\n"
        f"Проаналізуй ситуацію та запропонуй:\n"
        f"- Позицію (LONG або SHORT)\n"
        f"- Точку входу, тейк-профіт та стоп-лосс\n"
        f"- Орієнтовну тривалість угоди (в годинах)\n"
        f"- Стисле пояснення українською мовою"
    )


async def generate_signal_description(
    symbol: str,
    timeframe: str,
    rsi: float,
    sma: float,
    ema: float,
    macd: float,
    macd_signal: float,
    bb_upper: float,
    bb_lower: float,
    trend: str,
    support: float,
    resistance: float,
    price: float
) -> str:
    prompt = build_prompt(
        symbol, timeframe, rsi, sma, ema, macd, macd_signal,
        bb_upper, bb_lower, trend, support, resistance, price
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Ти досвідчений крипто-аналітик."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 500
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_URL, headers=headers, json=body) as response:
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Помилка LLM: {e}"