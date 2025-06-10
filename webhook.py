from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from services.market_data import get_crypto_prices
from services.groq_client import ask_groq

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши /analyze щоб почати.")

async def analyze_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Bitcoin (BTC)", callback_data="analyze_BTC")],
        [InlineKeyboardButton("Ethereum (ETH)", callback_data="analyze_ETH")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть монету для аналізу:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    symbol = query.data.split("_")[1]
    prices = get_crypto_prices([symbol])
    price = prices.get(symbol)

    if not price:
        await query.edit_message_text("Не вдалося отримати ціну.")
        return

    prompt = f"Поточна ціна {symbol} становить ${price:.2f}. Зроби короткий технічний аналіз і поради щодо входу/виходу (UA)."
    analysis = ask_groq(prompt)

    await query.edit_message_text(f"📊 Аналіз для {symbol}:\n\n{analysis}")

# Обробники, які підключаються в main.py
start = CommandHandler("start", start_callback)
analyze = CommandHandler("analyze", analyze_callback)
button_handler = CallbackQueryHandler(button_callback)