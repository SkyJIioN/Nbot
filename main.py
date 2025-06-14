from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application
from webhook import webhook_handler, application

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.initialize()
    await application.process_update(update)
    return {"ok": True}