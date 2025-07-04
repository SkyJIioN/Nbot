import os
from telegram.ext import ApplicationBuilder

# Завантаження токена з середовища (Render -> Environment)
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не встановлений у середовищі!")

# Створення Telegram Application
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()