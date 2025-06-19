from telegram.ext import CallbackQueryHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers.analyze import analyze_command, handle_symbol_input
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

app_telegram = ApplicationBuilder().token(TOKEN).build()

# Обробник команди /analyze
app_telegram.add_handler(CommandHandler("analyze", analyze_command))

# Обробник введення назви монети
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_input))

app_telegram.add_handler(CallbackQueryHandler(handle_timeframe_selection, pattern="^tf_"))