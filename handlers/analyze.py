from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from services.market_data import fetch_market_data
from services.groq_client import ask_groq


async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()

    await update.message.reply_text(f"Аналізую {symbol} на таймфреймі 4 години...")

    market_data = fetch_market_data(symbol)
    if not market_data:
        await update.message.reply_text("Не вдалося отримати ринкові дані. Спробуйте пізніше.")
        return

    prompt = (
        f"Проаналізуй ринкові дані криптовалюти {symbol} на основі наступних OHLCV-даних:\n"
        f"{market_data}\n"
        "Відповідай коротко українською. Вкажи чи варто відкривати long або short позицію, "
        "де орієнтовна точка входу та виходу. Не пиши зайвого тексту, тільки висновок."
    )

    result = ask_groq(prompt)
    await update.message.reply_text(result)


analyze_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_input)