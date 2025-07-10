from fastapi import FastAPI
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers.scan import scan_command, handle_scan_input
from webhook import webhook_router
import os

# Ініціалізуємо FastAPI
app = FastAPI()

# Отримуємо токен з оточення
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Створюємо Telegram Application
app_telegram = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()


@app.on_event("startup")
async def on_startup():
    await app_telegram.initialize()
    print("✅ Telegram Application initialized")

    # Додаємо обробники
    app_telegram.add_handler(CommandHandler("scan", scan_command))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_scan_input))

    print("✅ Handlers додано")


# Роут для Telegram Webhook
app.include_router(webhook_router)


@app.get("/")
async def root():
    return {"message": "🚀 Bot is running"}