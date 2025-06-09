from telegram import Update
from telegram.ext import ContextTypes
from services.binance_data import get_crypto_prices
from services.groq_client import ask_groq

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли /analyze для аналізу ринку.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Очікую дані з біржі...")

    prices = get_crypto_prices()
    if not prices:
        await update.message.reply_text("❌ Помилка отримання цін з Binance.")
        return

    btc = prices.get("BTCUSDT")
    eth = prices.get("ETHUSDT")

    if btc is None or eth is None:
        await update.message.reply_text("❌ Невідомі ціни з Binance.")
        return

    prompt = (
        f"Ціна BTC: {btc}$\n"
        f"Ціна ETH: {eth}$\n"
        "Чи варто входити в позицію на 1H графіку для BTC або ETH?\n"
        "Дай короткий технічний аналіз. Українською мовою. До 3 речень."
    )

    try:
        response = ask_groq(prompt)
        await update.message.reply_text(f"📊 Аналіз:\n{response}")
    except Exception as e:
        await update.message.reply_text("❌ Помилка від Groq API.")