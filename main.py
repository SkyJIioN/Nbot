from fastapi import FastAPI
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from webhook import webhook_router
from handlers.scan import scan_command, handle_coin_list

# Створюємо FastAPI додаток
app = FastAPI()

# Створюємо Telegram Application
app_telegram = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

# Обробник запуску FastAPI
@app.on_event("startup")
async def on_startup():
    await app_telegram.initialize()
    print("✅ Telegram Application initialized")

    # Реєстрація команд
    app_telegram.add_handler(CommandHandler("scan", scan_command))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_coin_list))

# Підключення маршруту вебхука
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "Bot is running"}