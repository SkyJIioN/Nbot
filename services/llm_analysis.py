# llm_analysis.py
import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance, price):
    return f"""
Криптовалюта: {symbol}
Таймфрейм: {timeframe.upper()}

Індикатори:
- Поточна ціна: {price:.2f}
- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}
- MACD Signal: {macd_signal:.2f}
- Bollinger Bands: Верхня {bb_upper:.2f}, Нижня {bb_lower:.2f}
- Тренд: {trend}
- Лінія підтримки: {support:.2f}
- Лінія опору: {resistance:.2f}

Зроби короткий технічний аналіз і сформуй рекомендацію у такому форматі:

- Позиція: LONG або SHORT
- Точка входу:
- Стоп-лосс:
- Тейк-профіт:
- Рекомендоване кредитне плече:
- Орієнтовний час відпрацювання в годинах:
- Опис ринкової ситуації: коротко оцінити індикатори

Відповідай лаконічно українською мовою.
"""


async def generate_signal_description(
    symbol,
    timeframe,
    rsi,
    sma,
    ema,
    macd,
    macd_signal,
    bb_upper,
    bb_lower,
    trend,
    support,
    resistance,
    price
):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "Ти досвідчений трейдер-аналітик. Відповідай коротко українською."
            },
            {
                "role": "user",
                "content": build_prompt(
                    symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                    bb_upper, bb_lower, trend, support, resistance, price
                )
            }
        ],
        "temperature": 0.4
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Помилка від Groq: {e}"