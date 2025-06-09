# handlers.py
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from services.market_data import get_crypto_prices
from services.groq_client import ask_groq

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли /analyze, щоб отримати аналіз ринку 🧠")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    await message.reply_text("⏳ Очікую дані...")

    prices = get_crypto_prices()
    logger.info(f"[DEBUG] Prices: {prices}")

    if not prices or not prices.get("bitcoin") or not prices.get("ethereum"):
        await message.reply_text("Не вдалося отримати ціну криптовалют.")
        return

    btc = prices["bitcoin"]
    eth = prices["ethereum"]

    prompt = (
        f"Зараз ціни:
BTC: {btc}$
ETH: {eth}$\n"
        f"Чи варто входити в позицію? Аналізуй 1H графік. "
        f"Відповідай українською коротко, до 3 речень, з технічним обґрунтуванням."
    )

    answer = ask_groq(prompt)
    logger.info(f"[DEBUG] Answer from Groq: {answer}")

    await message.reply_text(f"📊 Аналіз:
{answer}")

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analyze", analyze))
