from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext
from services.market_data import get_crypto_prices
from services.groq_client import ask_groq

start = CommandHandler("start", lambda u, c: u.message.reply_text("Привіт! Обери монету для аналізу: /analyze"))

async def analyze(update: Update, context: CallbackContext):
    prices = get_crypto_prices(["BTC", "ETH"])
    if not prices:
        await update.message.reply_text("Не вдалося отримати ціни.")
        return

    response_msg = "Оберіть монету для аналізу:"
    buttons = [
        [InlineKeyboardButton("BTC", callback_data="analyze_BTC")],
        [InlineKeyboardButton("ETH", callback_data="analyze_ETH")]
    ]
    await update.message.reply_text(response_msg, reply_markup=InlineKeyboardMarkup(buttons))