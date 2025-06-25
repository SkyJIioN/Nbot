import os
import requests

def generate_analysis_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, current_price, volume):
    return f"""
📊 Аналіз криптовалюти {symbol} на таймфреймі {timeframe.upper()}:

Поточна ціна: {current_price:.2f}$
Обʼєм торгів: {volume}

Індикатори:
- RSI: {rsi:.2f}
- SMA: {sma:.2f}
- EMA: {ema:.2f}
- MACD: {macd:.2f}
- MACD Signal: {macd_signal:.2f}

На основі цих даних:
1. Вкажи торгову рекомендацію: LONG, SHORT або WAIT
2. Вкажи точку входу й ціль для виходу
3. Коротко поясни, чому саме така рекомендація
"""

def get_llm_recommendation(symbol, timeframe, rsi, sma, ema, macd, macd_signal, current_price, volume):
    prompt = generate_analysis_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, current_price, volume)

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Ти досвідчений трейдер-аналітик, який коротко і чітко дає рекомендації."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("LLM Error:", response.text)
        return "⚠️ Не вдалося отримати відповідь від ШІ."
