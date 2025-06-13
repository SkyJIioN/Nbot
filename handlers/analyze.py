from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters
from services.market_data import get_crypto_price
from services.groq_client import ask_groq

async def analyze_symbol(symbol: str) -> str:
    price = await get_price(symbol)
    if price is None:
        return f"Не вдалося отримати ціну для {symbol.upper()}."
    prompt = f"Проаналізуй криптовалюту {symbol.upper()} з поточною ціною {price} USD. Дай рекомендації по входу/виходу."
    reply = await ask_groq(prompt)
    return f"Ціна {symbol.upper()}: {price} USD\n\n{reply}"

async def handle_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    result = await analyze_symbol(symbol)
    await update.message.reply_text(result)

handle_symbol_input = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol)
