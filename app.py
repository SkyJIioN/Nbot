# app.py

import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from handlers.analyze import analyze_command, handle_symbol_input, handle_timeframe_selection

TOKEN = os.getenv("TELEGRAM_TOKEN")

app_telegram = ApplicationBuilder().token(TOKEN).build()

# Обробник команди /analyze
app_telegram.add_handler(CommandHandler("analyze", analyze_command))

# Обробник введення символу монети
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_input))

# Обробник вибору таймфрейму
app_telegram.add_handler(CallbackQueryHandler(handle_timeframe_selection, pattern="^tf_"))