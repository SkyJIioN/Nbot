import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers.analyze import analyze_command, handle_symbol_input

application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

application.add_handler(CommandHandler("start", analyze_command))
application.add_handler(CommandHandler("analyze", analyze_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_input))

webhook_handler = application