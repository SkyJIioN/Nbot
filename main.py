import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application

from webhook import application as app_telegram

app = FastAPI()


@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, app_telegram.bot)
    await app_telegram.process_update(update)
    return {"status": "ok"}