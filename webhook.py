import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

from services.market_data import get_price
from services.groq_client import ask_groq

TOKEN = os.getenv("TELEGRAM_TOKEN")

application = Application.builder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
    [InlineKeyboardButton("Bitcoin", callback_data="BTC")],
    [InlineKeyboardButton("Ethereum", callback_data="ETH")],
    [InlineKeyboardButton("Solana", callback_data="SOL")],
    [InlineKeyboardButton("BNB", callback_data="BNB")],
    [InlineKeyboardButton("Dogecoin", callback_data="DOGE")],
]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть монету для аналізу:", reply_markup=reply_markup)


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    coin = query.data

    await query.edit_message_text("Збираю дані...")

    try:
        price = get_price(coin)
        prompt = (
            f"Короткий аналіз монет {coin.upper()} з ціною {price}$.\n"
            f"Поради: де увійти, де вийти, поточний тренд. Стислі поради українською мовою."
        )
        reply = ask_groq(prompt)
        await query.edit_message_text(reply)
    except Exception as e:
        await query.edit_message_text("Не вдалося отримати дані. Спробуйте пізніше.")
        print("Error:", e)


application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(analyze))
