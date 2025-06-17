import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"  # Актуальна модель, оскільки mixtral більше не підтримується

def ask_groq(symbol: str, indicators: dict) -> str:
    prompt = (
        f"На основі наступних індикаторів для {symbol} на 4-годинному таймфреймі:\n"
        f"- Поточна ціна: {indicators['current_price']}\n"
        f"- RSI (14): {indicators['RSI_14']}\n"
        f"- SMA (14): {indicators['SMA_14']}\n\n"
        "Зроби короткий аналіз українською мовою. "
        "Дай рекомендацію щодо відкриття позиції (Long або Short), "
        "та вкажи орієнтовні точки входу і виходу. "
        "Без зайвих пояснень, лише чітка порада."
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Groq error:", e)
        return "Виникла помилка при зверненні до Groq."