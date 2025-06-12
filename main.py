from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application
from webhook import application as app_telegram  # це ApplicationBuilder().token(...).build()

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, app_telegram.bot)

        # Ініціалізація додатку
        if not app_telegram._initialized:
            await app_telegram.initialize()
            await app_telegram.start()

        await app_telegram.process_update(update)
        return {"ok": True}
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"ok": False, "error": str(e)}
