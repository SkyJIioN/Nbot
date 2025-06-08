import logging
from fastapi import APIRouter, Request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters
)
from services.market_data import get_crypto_prices
from services.groq_client import ask_groq

import os

TOKEN = os.getenv("BOT_TOKEN")  # обов'язково встановити в Render secrets

router = APIRouter()
app_telegram = Application.builder().token(TOKEN).build()

@router.post("/webhook")
async def process_webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, app_telegram.bot)
    await app_telegram.initialize()
    await app_telegram.process_update(update)
    return {"ok": True}

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = get_crypto_prices(["bitcoin", "ethereum"])
    await update.message.reply_text(f"DEBUG: {prices}")

app_telegram.add_handler(CommandHandler("debug", debug))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Натисни /analyze для аналізу криптовалют.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = get_crypto_prices(["bitcoin", "ethereum"])
    if not prices:
        await update.message.reply_text("Помилка отримання даних з CoinGecko.")
        return

    btc_price = prices.get("bitcoin")
    eth_price = prices.get("ethereum")

    prompt = (
        f"Ціна BTC: ${btc_price}, ETH: ${eth_price}. "
        "Дай короткий технічний аналіз і вкажи приблизні точки входу і виходу."
    )
    analysis = ask_groq(prompt)

    message = f"""📊 Аналіз ринку:
BTC: ${btc_price}
ETH: ${eth_price}

🤖 ШІ: {analysis}"""
    await update.message.reply_text(message)

# Реєстрація обробників
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", analyze))