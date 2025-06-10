from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application
import os
from dotenv import load_dotenv
from webhook import start, analyze

load_dotenv()

app = FastAPI()

application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
application.add_handler(start)
application.add_handler(analyze)

@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=os.getenv("WEBHOOK_URL"))

@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return {"ok": True}