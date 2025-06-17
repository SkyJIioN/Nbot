from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application
from webhook import app_telegram, webhook_handler

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    update = Update.de_json(await request.json(), app_telegram.bot)
    await app_telegram.process_update(update)
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Bot is live"}

