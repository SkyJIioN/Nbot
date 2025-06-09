import requests
import logging

logger = logging.getLogger(__name__)

GROQ_API_KEY = "тут_твій_groq_api_key"

def ask_groq(prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        json_data = response.json()
        logger.debug(f"GROQ response: {json_data}")  # Додаємо лог

        if "choices" in json_data:
            return json_data["choices"][0]["message"]["content"]
        else:
            return "❌ Groq API не повернув відповідь."
    except Exception as e:
        logger.error(f"Помилка при запиті до Groq: {e}")
        return "❌ Сталася помилка при зверненні до Groq API."