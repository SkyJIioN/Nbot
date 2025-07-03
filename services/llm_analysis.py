import os
import requests
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                 bb_upper, bb_lower, trend, support, resistance):
    return f"""
🔍 Аналіз криптовалюти {symbol} на таймфреймі {timeframe.upper()} з технічними індикаторами:
- Поточний тренд: {trend}
- Лінія підтримки: {support:.2f}$
- Лінія опору: {resistance:.2f}$
- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}
- MACD Signal: {macd_signal:.2f}
- Bollinger Bands: Верхня {bb_upper:.2f}, Нижня {bb_lower:.2f}

На основі цих даних:
1. Опиши стан ринку (перекупленість, нейтральність, перепроданість).
2. Зроби лаконічну рекомендацію: LONG, SHORT або Очікувати.
3. Запропонуй:
   - Точку входу
   - Тейк-профіт
   - Стоп-лосс
   - Орієнтовний час (в годинах)
   - Рекомендоване кредитне плече

Відповідь українською, структуровано у такому форматі:
- Позиція: LONG/SHORT
- Точка входу: 
- Тейк-профіт:
- Стоп-лосс:
- Орієнтовний час:
- Кредитне плече:
- Опис ринкової ситуації:
"""

async def generate_signal_description(symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                                      bb_upper, bb_lower, trend, support, resistance):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "Ти досвідчений крипто-трейдер. Відповідай чітко, українською мовою, без зайвих деталей."
            },
            {
                "role": "user",
                "content": build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                                        bb_upper, bb_lower, trend, support, resistance)
            }
        ],
        "temperature": 0.4
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Помилка від Groq: {e}"