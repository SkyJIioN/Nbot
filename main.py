from fastapi import FastAPI
from handlers.scan import scan_command
from webhook import webhook_router
from app import app_telegram
from telegram.ext import CommandHandler
import os

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Додаємо хендлер
    app_telegram.add_handler(CommandHandler("scan", scan_command))

    # Ініціалізуємо Application
    await app_telegram.initialize()

    # Встановлюємо Webhook
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("WEBHOOK_URL is not set!")
    await app_telegram.bot.set_webhook(url=webhook_url + "/webhook")
    print(f"✅ Webhook встановлено: {webhook_url}/webhook")

# Підключаємо маршрут
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "Bot is running"}