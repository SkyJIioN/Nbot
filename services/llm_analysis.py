import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance):
    return f"""
Технічний аналіз криптовалюти {symbol} на таймфреймі {timeframe.upper()}:

- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}, сигнальна: {macd_signal:.2f}
- Bollinger Bands: Верхня межа {bb_upper:.2f}, нижня межа {bb_lower:.2f}
- Тренд: {trend}
- Лінія підтримки: {support:.2f}
- Лінія опору: {resistance:.2f}

На основі цих індикаторів:
1. Сформулюй поточну ринкову ситуацію.
2. Визнач оптимальну позицію (LONG або SHORT).
3. Запропонуй точку входу, тейк-профіт, стоп-лосс.
4. Оціни орієнтовний час відпрацювання (в годинах).
5. Відповідай українською стисло та структуровано у форматі:

- Позиція: LONG або SHORT
- Точка входу:
- Тейк-профіт:
- Стоп-лосс:
- Орієнтовний час:
- Опис ринкової ситуації:
"""

async def generate_signal_description(symbol, timeframe, rsi, sma, ema, macd, macd_signal, trend, support, resistance, bb_upper, bb_lower):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "Ти досвідчений трейдер-аналітик. Відповідай стисло та українською."
            },
            {
                "role": "user",
                "content": build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance)
            }
        ],
        "temperature": 0.3
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