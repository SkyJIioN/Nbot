import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def build_prompt(symbol, timeframe, price, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance):
    return f"""
Ти професійний трейдер. Проаналізуй ситуацію для криптовалюти {symbol} на таймфреймі {timeframe.upper()}.

Дані:
- Поточна ціна: {price:.2f}
- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}
- MACD Signal: {macd_signal:.2f}
- Bollinger Bands: Верхня {bb_upper:.2f}, Нижня {bb_lower:.2f}
- Тренд: {trend}
- Підтримка: {support:.2f}, Опір: {resistance:.2f}

На основі цих даних:
1. Визнач позицію: LONG або SHORT
2. Запропонуй точку входу
3. Запропонуй стоп-лосс
4. Запропонуй тейк-профіт
5. Орієнтовний час утримання позиції в годинах
6. Рекомендоване кредитне плече (якщо доречно)

❗️ Відповідай чітко у форматі:
- Позиція: 
- Точка входу: 
- Стоп-лосс: 
- Тейк-профіт: 
- Орієнтовний час: 
- Плече: 

Мова відповіді: українська
"""


async def generate_signal_description(symbol, timeframe, price, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "Ти досвідчений трейдер-аналітик. Відповідай чітко та коротко українською мовою."
            },
            {
                "role": "user",
                "content": build_prompt(symbol, timeframe, price, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance)
            }
        ],
        "temperature": 0.4
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Помилка від Groq: {e}"