from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers.analyze import analyze_command, handle_symbol_input
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

app_telegram = Application.builder().token(BOT_TOKEN).build()

app_telegram.add_handler(CommandHandler("start", analyze_command))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_input))
