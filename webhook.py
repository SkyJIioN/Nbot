from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from services.market_data import get_crypto_prices
from services.groq_client import ask_groq

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Аналізувати BTC/ETH", callback_data="analyze")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привіт! Обери монету для аналізу:", reply_markup=reply_markup)

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Очікую дані...")

    prices = get_crypto_prices()
    if not prices:
        await query.edit_message_text("Помилка при отриманні цін з Binance")
        return

    prompt = f"Зроби короткий аналіз BTC і ETH на основі поточних цін: BTC = {prices.get('btcusdt')} USD, ETH = {prices.get('ethusdt')} USD. Які точки входу/виходу?"
    answer = ask_groq(prompt)
    await query.edit_message_text(answer)

# Хендлери
start = CommandHandler("start", start)
analyze = CallbackQueryHandler(analyze, pattern="^analyze$")
