import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance):
    return f"""
Аналіз криптовалюти {symbol} на таймфреймі {timeframe.upper()}:

Технічні індикатори:
- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}
- MACD Signal: {macd_signal:.2f}
- Bollinger Bands: Верхня межа {bb_upper:.2f}, Нижня межа {bb_lower:.2f}
- Тренд: {trend.capitalize()}
- Лінія підтримки: {support:.2f}
- Лінія опору: {resistance:.2f}

Зроби короткий технічний аналіз і надай:
- Стан ринку (перекупленість, перепроданість, нейтральний)
- Чітку рекомендацію: LONG, SHORT або Очікувати
- Обґрунтування на 1-2 речення
- Прогноз точки входу, стоп-лоссу, тейк-профіту
- Рекомендоване кредитне плече та час утримання (у годинах)

Відповідай українською. Формат відповіді:
- Позиція: 
- Точка входу: 
- Тейк-профіт: 
- Стоп-лосс: 
- Орієнтовний час: 

Опис ринкової ситуації:
"""


async def generate_signal_description(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance):
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
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Помилка від Groq: {e}"