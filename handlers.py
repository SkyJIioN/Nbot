from telegram import Update
from telegram.ext import ContextTypes

from services.market_data import get_crypto_price
from services.groq_client import ask_groq

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть символ монети, наприклад BTC або ETH.")

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()

    try:
        price = get_crypto_price(symbol)
        if price is None:
            await update.message.reply_text(f"Не вдалося знайти ціну для {symbol}.")
            return

        prompt = (
            f"Зроби короткий технічний аналіз для монети {symbol} при поточній ціні {price}$.\n"
            f"Вкажи точки входу, виходу, рівні підтримки та опору. Додай рекомендацію."
        )

        analysis = ask_groq(prompt)
        await update.message.reply_text(analysis)
    except Exception as e:
        await update.message.reply_text("Сталася помилка при обробці запиту.")
        print(f"Error in handle_symbol_input: {e}")