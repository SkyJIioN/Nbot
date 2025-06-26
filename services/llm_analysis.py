import os
import requests
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "тут_твій_ключ"  # заміни тут ключ

def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal):
    return f"""
Аналіз криптовалюти {symbol} на таймфреймі {timeframe.upper()} з технічними індикаторами:
- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}
- MACD Signal: {macd_signal:.2f}

На основі цих даних:
1. Опиши ринкову ситуацію (перекупленість, нейтрально, перепроданість).
2. Дай коротку рекомендацію: LONG, SHORT або Очікувати.
"""

def generate_signal_description(symbol, timeframe, rsi, sma, ema, macd, macd_signal):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal)

    payload = {
        "model": "llama3-70b-8192" 
        "messages": [
            {"role": "system", "content": "Ти досвідчений трейдер. Відповідай коротко українською."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }

    try:
        print("🔍 Payload що відправляється:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

        print("📨 Відповідь API:")
        print(response.status_code)
        print(response.text)

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except requests.exceptions.HTTPError as e:
        return f"⚠️ Помилка від Groq: {e}"
    except Exception as e:
        return f"⚠️ Невідома помилка: {e}"