### Структура проекту:
# crypto_ai_bot/
# ├── main.py
# └── services/
#     ├── __init__.py
#     ├── market_data.py
#     └── groq_client.py

# --- main.py ---
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
import logging

from handlers import start, analyze, error_handler

# Ініціалізація
app = FastAPI()
TOKEN = "тут_твій_токен"

app_telegram = ApplicationBuilder().token(TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", analyze))
app_telegram.add_error_handler(error_handler)

@app.on_event("startup")
async def startup():
    await app_telegram.initialize()
    print("✅ Telegram Application Initialized")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, app_telegram.bot)
        await app_telegram.process_update(update)
        return {"ok": True}
    except Exception as e:
        logging.exception(f"Виняток при обробці оновлення: {e}")
        return {"ok": False}

# --- / endpoint ---
@app.get("/")
def home():
    return {"status": "ok"}

# --- Обробники ---
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", analyze))
app_telegram.add_error_handler(error_handler)

# --- services/__init__.py ---
# (залишити порожнім)

# --- services/market_data.py ---
import requests

def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,dogecoin",
        "vs_currencies": "usd"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "BTC": data.get("bitcoin", {}).get("usd", "н/д"),
            "ETH": data.get("ethereum", {}).get("usd", "н/д"),
            "DOGE": data.get("dogecoin", {}).get("usd", "н/д"),
        }
    except Exception as e:
        print(f"Помилка отримання цін: {e}")
        return {"BTC": "н/д", "ETH": "н/д", "DOGE": "н/д"}

# --- services/groq_client.py ---
import requests
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_groq(prompt):
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
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Помилка при запиті до Groq: {e}")
        return "⚠️ Не вдалося отримати відповідь від ШІ."
