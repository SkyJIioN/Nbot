from fastapi import FastAPI
from handlers.scan import scan_command
from webhook import webhook_router
from app import app_telegram  # Імпортуємо Application
import asyncio

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # 🔄 Ініціалізуємо Telegram Application при запуску FastAPI
    await app_telegram.initialize()
    print("✅ Telegram Application initialized")

application.add_handler(CommandHandler("scan", scan_command)

# Підключаємо маршрут вебхука
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "Bot is running"}