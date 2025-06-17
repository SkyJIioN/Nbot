from fastapi import FastAPI
from webhook import webhook_router
from app import app_telegram  # Об'єкт Application з telegram.ext

app = FastAPI()

# Підключаємо маршрути обробки Telegram webhook
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "Bot is running"}