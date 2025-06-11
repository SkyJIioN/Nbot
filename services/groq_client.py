import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_groq(message: str) -> str:
    if not GROQ_API_KEY:
        return "❌ GROQ API ключ не встановлено."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",  # або llama3-8b-8192, якщо бажаєш
        "messages": [
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)

    # Вивід для дебагу:
    if response.status_code != 200:
        print("Groq response:", response.text)

    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]