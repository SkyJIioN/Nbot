from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import get_crypto_prices
from services.groq_client import ask_groq

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Надішли /analyze для аналізу крипторинку.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Очікую дані...")

    prices = get_crypto_prices()
    if not prices:
        await update.message.reply_text("❌ Не вдалося отримати ринкові дані.")
        return

    btc = prices.get("bitcoin", "н/д")
    eth = prices.get("ethereum", "н/д")

    prompt = (
        f"Ціна BTC/USDT: {btc}$, ETH/USDT: {eth}$.\n"
        "Чи варто входити в позицію зараз на 1H графіку?\n"
        "Відповідай коротко українською мовою, технічно."
    )

    result = ask_groq(prompt)
    await update.message.reply_text(f"📊 Відповідь ШІ:\n{result}")