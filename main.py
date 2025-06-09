import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from webhook import start, analyze

BOT_TOKEN = os.getenv("TG_TOKEN")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

app = FastAPI()
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("analyze", analyze))

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}