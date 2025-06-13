from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application
from handlers.analyze import handle_symbol_input
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = FastAPI()

app_telegram = Application.builder().token(BOT_TOKEN).build()
app_telegram.add_handler(handle_symbol_input)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, app_telegram.bot)
    await app_telegram.initialize()
    await app_telegram.process_update(update)
    return {"ok": True}