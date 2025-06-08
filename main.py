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
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import TypeHandler
import logging
import os
from services.market_data import get_crypto_prices
from services.groq_client import ask_groq

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI init ---
app = FastAPI()

# --- Telegram init ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-render-url.com/webhook

app_telegram = Application.builder().token(BOT_TOKEN).build()

# --- /start команда ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли /analyze для аналізу ринку.")

# --- /analyze команда ---
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = get_crypto_prices()
    prompt = (
        f"Поточні ціни:\n"
        + "\n".join([f"{sym}: ${price}" for sym, price in prices.items()])
        + "\n\nДай короткий аналіз (до 3 речень) і вкажи можливі точки входу/виходу. Українською."
    )
    response = ask_groq(prompt)
    await update.message.reply_text(f"📊 Аналіз ринку:\n{response}")

# --- Error handler ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Виняток при обробці оновлення:", exc_info=context.error)

# --- Webhook endpoint ---
@app.post("/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()
    update = Update.de_json(body, app_telegram.bot)
    await app_telegram.process_update(update)
    return {"ok": True}

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
