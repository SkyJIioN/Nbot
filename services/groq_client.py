import requests
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def analyze_with_groq(prices: dict) -> str:
    prompt = (
        "Проаналізуй ринок криптовалют на основі поточних цін:\n\n"
        + "\n".join([f"{symbol}: ${price:.2f}" for symbol, price in prices.items()])
        + "\n\nНадай короткий технічний аналіз з точками входу та виходу."
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # 👇 Перевірка наявності 'choices'
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "❌ Не вдалося отримати відповідь від Groq."
    except Exception as e:
        return f"❌ Помилка Groq: {e}"