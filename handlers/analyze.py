from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import get_crypto_price
from services.groq_client import ask_groq

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Введи символ монети (наприклад: BTC, ETH, SOL)")

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    try:
        price = get_crypto_price(symbol)
        if price is None:
            raise ValueError("Неможливо отримати ціну")
        prompt = f"Зараз ціна {symbol} становить {price} доларів. Зроби короткий технічний аналіз та рекомендації."
        reply = ask_groq(prompt)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка: {str(e)}")
