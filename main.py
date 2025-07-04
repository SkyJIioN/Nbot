import os
from fastapi import FastAPI
from telegram.ext import Application, CommandHandler
from webhook import webhook_router
from handlers.scan import scan_command
from dotenv import load_dotenv

load_dotenv()  # читає .env, не заважає якщо запускаєш локально

# Отримуємо токен із змінної середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено. Перевір змінну середовища у Render.")

# Ініціалізуємо Telegram Application
app_telegram = Application.builder().token(BOT_TOKEN).build()

# FastAPI додаток
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Додаємо хендлери
    app_telegram.add_handler(CommandHandler("scan", scan_command))

    # Ініціалізація Telegram Webhook
    await app_telegram.initialize()
    print("✅ Telegram Application initialized")

# Підключаємо webhook маршрут
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "🤖 Bot is running!"}