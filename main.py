from fastapi import FastAPI, Request
from webhook import webhook_handler
from app import app_telegram

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    update_data = await request.json()
    await webhook_handler(update_data, app_telegram)
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Nbot is running"}