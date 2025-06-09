from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder
from webhook import start, analyze
from config import TELEGRAM_TOKEN

app = FastAPI()

app_telegram = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app_telegram.add_handler(start)
app_telegram.add_handler(analyze)

@app.on_event("startup")
async def startup():
    await app_telegram.initialize()
    print("✅ Telegram bot initialized")

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, app_telegram.bot)
    await app_telegram.process_update(update)
    return {"ok": True}

@app.get("/")
def root():
    return {"status": "Bot is running!"}
