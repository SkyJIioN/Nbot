import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from services.market_data import get_btc_price
from services.groq_client.py import ask_groq

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://your-render-url.onrender.com{WEBHOOK_PATH}"

app = FastAPI()
telegram_app = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Надішли /analyze для аналізу BTC.")

# Команда /analyze
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = get_btc_price()
        prompt = (
            f"Ціна BTC/USDT зараз {price}$. "
            "Чи варто входити в позицію на 1H графіку? "
            "Дай коротку відповідь (до 3 речень), аргументуй технічно. "
            "Відповідай українською мовою."
        )
        answer = ask_groq(prompt)
        await update.message.reply_text(f"📊 Поточна ціна BTC: ${price}\n\n🤖 {answer}")
    except Exception as e:
        logging.error(f"Помилка аналізу: {e}")
        await update.message.reply_text("⚠️ Сталася помилка під час аналізу.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("analyze", analyze))

@app.on_event("startup")
async def startup():
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    telegram_app.initialize()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    await telegram_app.process_update(Update.de_json(await req.json(), telegram_app.bot))
    return {"ok": True}
