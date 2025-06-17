from telegram.ext import ApplicationBuilder
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()