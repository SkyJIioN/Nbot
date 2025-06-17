from fastapi import APIRouter, Request
from telegram import Update
from app import app_telegram  # Об'єкт Application з telegram.ext
import asyncio

router = APIRouter()

@router.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    update = Update.de_json(data, app_telegram.bot)
    asyncio.create_task(app_telegram.process_update(update))
    return {"status": "ok"}