# main.py

from fastapi import FastAPI
from handlers.scan import scan_command
from webhook import webhook_router
from app import app_telegram  # Імпортуємо Application
from telegram.ext import CommandHandler

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    # 🔄 Ініціалізуємо Telegram Application при запуску FastAPI
    await app_telegram.initialize()
    app_telegram.add_handler(CommandHandler("scan", scan_command))
    print("✅ Telegram Application initialized")


# Підключаємо маршрут вебхука
app.include_router(webhook_router)


@app.get("/")
async def root():
    return {"message": "Bot is running"}