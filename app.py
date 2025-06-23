from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from handlers.analyze import analyze_command, handle_symbol_input, handle_timeframe_selection
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

app_telegram = ApplicationBuilder().token(TOKEN).build()

# Команда /analyze
app_telegram.add_handler(CommandHandler("analyze", analyze_command))

# Обробка введення монети (наприклад BTC, ETH)
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_input))

# Обробка вибору таймфрейму
app_telegram.add_handler(CallbackQueryHandler(handle_timeframe_selection, pattern="^tf_"))