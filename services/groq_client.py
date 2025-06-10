import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "mixtral-8x7b-32768"

def ask_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=json_data)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"]