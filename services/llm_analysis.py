import os
import requests
import numpy as np

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Захист від NaN, None, inf
def safe_format(value):
    try:
        if value is None or isinstance(value, str):
            return "N/A"
        if np.isnan(value) or np.isinf(value):
            return "N/A"
        return f"{value:.2f}"
    except:
        return "N/A"

def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal):
    return f"""
Аналіз криптовалюти {symbol} на таймфреймі {timeframe.upper()} з технічними індикаторами:
- RSI: {safe_format(rsi)}
- SMA: {safe_format(sma)}
- EMA: {safe_format(ema)}
- MACD: {safe_format(macd)}
- MACD Signal: {safe_format(macd_signal)}

На основі цих даних коротко (1-2 речення) оціни ситуацію:
1. Опиши стан ринку (наприклад, перекупленість, нейтрально, перепроданість).
2. Зроби рекомендацію: LONG, SHORT або Очікувати.
"""

# 🔁 Функція СИНХРОННА, бо requests — не async
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