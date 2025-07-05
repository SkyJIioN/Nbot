import os
import aiohttp
import asyncio

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance, price):
    return f"""
Ціна {symbol}: {price} USD
Технічні індикатори на таймфреймі {timeframe.upper()}:
- RSI: {rsi:.5f}
- SMA: {sma:.5f}
- EMA: {ema:.5f}
- MACD: {macd:.5f}
- MACD Signal: {macd_signal:.5f}
- Bollinger Bands: Верхня {bb_upper:.5f}, Нижня {bb_lower:.5f}
- Тренд: {trend}
- Лінія підтримки: {support:.5f}, Лінія опору: {resistance:.5f}

На основі цих даних, зроби короткий технічний аналіз і сформуй чітку торгову стратегію.
Відповідай у форматі JSON:
{{
  "position": "LONG або SHORT",
  "entry_price": "Ціна входу",
  "take_profit": "Цільова ціна",
  "stop_loss": "Стоп-лосс",
  "leverage": "Рекомендоване плече",
  "duration_hours": "Орієнтовний час у годинах",
  "comment": "Короткий опис ринку українською"
}}
Відповідай лише JSON, без пояснень.
"""


async def generate_signal_description(symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                                      bb_upper, bb_lower, trend, support, resistance, price):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Ти професійний трейдер-аналітик. Відповідай лише JSON без пояснень."},
            {"role": "user", "content": build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                                                         bb_upper, bb_lower, trend, support, resistance, price)}
        ],
        "temperature": 0.4
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.groq.com/openai/v1/chat/completions",
                                    headers=headers, json=payload, timeout=15) as response:
                response.raise_for_status()
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                return content.strip()
    except Exception as e:
        return f"⚠️ Помилка від Groq: {e}"