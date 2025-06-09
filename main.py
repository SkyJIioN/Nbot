from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, CommandHandler
import os
import logging
from webhook import start, analyze

TOKEN = os.getenv("BOT_TOKEN")

app_telegram = ApplicationBuilder().token(TOKEN).build()

app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", analyze))

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, app_telegram.bot)
    await app_telegram.process_update(update)
    return {"status": "ok"}