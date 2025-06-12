### 📁 handlers/analyze.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.market_data import get_price
from services.groq_client import ask_groq

SUPPORTED_SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "DOGE"]

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(symbol, callback_data=f"analyze:{symbol}")]
                for symbol in SUPPORTED_SYMBOLS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть криптовалюту для аналізу:", reply_markup=reply_markup)


async def analyze_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, symbol = query.data.split(":")
    price = get_price(symbol)

    if price == 0.0:
        await query.edit_message_text(f"Не вдалося отримати ціну для {symbol}.")
        return

    prompt = f"Проаналізуй {symbol} з поточною ціною {price:.2f} USD. Які можливі точки входу/виходу? Напиши коротко українською."
    response = ask_groq(prompt)

    if not response:
        await query.edit_message_text("Не вдалося отримати відповідь від Groq.")
    else:
        await query.edit_message_text(f"{symbol} ({price:.2f} USD):\n{response}")
