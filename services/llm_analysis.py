import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, trend, support, resistance):
    return f"""
Аналіз криптовалюти {symbol} на таймфреймі {timeframe.upper()} з технічними індикаторами:
- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}
- MACD Signal: {macd_signal:.2f}
- Тренд: {trend}
- Лінія підтримки: {support:.2f}
- Лінія опору: {resistance:.2f}

На основі цих даних:
1. Опиши ринкову ситуацію (наприклад, перекупленість, нейтрально, трендовий рух).
2. Вкажи чітку рекомендацію: LONG, SHORT або Очікувати.
3. Запропонуй точку входу, тейк-профіт, стоп-лосс і орієнтовний час угоди в годинах.
Формат відповіді:
- Позиція: 
- Точка входу: 
- Тейк-профіт: 
- Стоп-лосс: 
- Орієнтовний час: 
"""

async def generate_signal_description(symbol, timeframe, rsi, sma, ema, macd, macd_signal, trend, support, resistance):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Ти досвідчений трейдер-аналітик. Відповідай коротко українською."},
            {"role": "user", "content": build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, trend, support, resistance)}
        ],
        "temperature": 0.4
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Помилка від Groq: {e}"