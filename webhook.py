from fastapi import APIRouter, Request, Depends
from telegram import Update
from telegram.ext import Application

from app import app_telegram  # Імпортуємо об'єкт Telegram Application

webhook_router = APIRouter()


@webhook_router.post("/webhook")
async def webhook_handler(request: Request, app: Application = Depends(lambda: app_telegram)):
    try:
        update_data = await request.json()
        update = Update.de_json(update_data, app.bot)
        await app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        print(f"Error handling webhook: {e}")
        return {"status": "error", "message": str(e)}