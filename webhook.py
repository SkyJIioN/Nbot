from fastapi import APIRouter, Request
from telegram import Update
from app import app_telegram  # Telegram Application
import asyncio

webhook_router = APIRouter()

@webhook_router.post("/webhook")
async def webhook_handler(request: Request):
    try:
        data = await request.json()
        print("🔔 Отримано новий update:", data)  
        update = Update.de_json(data, app_telegram.bot)

        # Ініціалізація Telegram Application (тільки 1 раз)
        if not app_telegram._initialized:
            await app_telegram.initialize()

        # 🧠 Обробка апдейту у фоновому режимі (асинхронний task)
        asyncio.create_task(app_telegram.process_update(update))

        # ✅ Відповідаємо Telegram швидко
        return {"status": "ok"}

    except Exception as e:
        print(f"Error handling webhook: {e}")
        return {"status": "error", "message": str(e)}