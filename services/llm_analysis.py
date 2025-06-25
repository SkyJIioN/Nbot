# llm_analysis.py
import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal):
    return f"""
Аналіз криптовалюти {symbol} на таймфреймі {timeframe.upper()} з технічними індикаторами:
- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}
- MACD Signal: {macd_signal:.2f}

На основі цих даних коротко (1-2 речення) оціни ситуацію:
1. Опиши стан ринку (наприклад, перекупленість, нейтрально, перепроданість).
2. Зроби рекомендацію: LONG, SHORT або Очікувати.
"""

def generate_signal_description(symbol, timeframe, rsi, sma, ema, macd, macd_signal):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {
                "role": "system",
                "content": "Ти досвідчений трейдер-аналітик. Відповідай коротко українською."
            },
            {
                "role": "user",
                "content": build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal)
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