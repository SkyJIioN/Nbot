import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance):
    return f"""
🔎 Аналіз криптовалюти {symbol} на таймфреймі {timeframe.upper()} з індикаторами:
- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}
- MACD Signal: {macd_signal:.2f}
- Bollinger Bands: Верхня {bb_upper:.2f}, Нижня {bb_lower:.2f}
- Тренд: {trend}
- Підтримка: {support:.2f}
- Опір: {resistance:.2f}

На основі цих даних:
1. Оціни ринкову ситуацію (перекупленість, перепроданість, нейтрально).
2. Зроби висновок: LONG, SHORT або Очікувати.
3. Запропонуй:
   - Точку входу
   - Стоп-лосс
   - Тейк-профіт
   - Орієнтовний час відпрацювання в годинах
   - Рекомендоване кредитне плече

Формат відповіді:
- Позиція: LONG або SHORT
- Точка входу: 
- Тейк-профіт: 
- Стоп-лосс: 
- Орієнтовний час: 
- Кредитне плече: 

Опис ринкової ситуації: [1-2 речення]
Відповідай лаконічно українською мовою.
"""


async def generate_signal_description(symbol, timeframe, rsi, sma, ema, macd, macd_signal, trend, support, resistance):
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
                "content": build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance)
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