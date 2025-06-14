from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import fetch_price
from services.groq_client import ask_groq

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть символ монети (наприклад, BTC):")

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()

    await update.message.reply_text("Отримую дані...")

    price = fetch_price(symbol)
    if not price:
        await update.message.reply_text("Не вдалося отримати ціну. Перевірте правильність символу.")
        return

    prompt = (
        f"Поточна ціна {symbol}: {price} USD.\n"
        f"Зроби короткий технічний аналіз і поради щодо входу/виходу для трейдера українською мовою."
    )

    response = ask_groq(prompt)
    if response:
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Помилка аналізу через Groq.")