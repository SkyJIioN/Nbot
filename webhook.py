from fastapi import APIRouter, Request
from telegram import Update

from app import app_telegram  # Імпортуємо Application

webhook_router = APIRouter()


@webhook_router.post("/webhook")
async def webhook_handler(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, app_telegram.bot)

        if not app_telegram._initialized:
            await app_telegram.initialize()  # <== ДОДАНО ЦЕ

        await app_telegram.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        print(f"Error handling webhook: {e}")
        return {"status": "error", "message": str(e)}