from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import fetch_market_data
from services.groq_client import ask_groq

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()

    await update.message.reply_text(
        f"Аналізую {symbol} на таймфреймі 4 години..."
    )

    # Отримання ринкових даних
    ohlcv_data = fetch_market_data(symbol)
    if ohlcv_data is None:
        await update.message.reply_text("Не вдалося отримати дані для аналізу.")
        return

    # Формування запиту до ШІ
    prompt = (
        f"Проаналізуй наступні 4-годинні OHLCV дані для {symbol}:\n\n{ohlcv_data}\n\n"
        "Зроби короткий технічний аналіз із зазначенням:\n"
        "- чи варто відкривати LONG або SHORT позицію,\n"
        "- приблизні точки входу, Take Profit і Stop Loss.\n"
        "Формат відповіді: 2-3 речення українською мовою."
    )

    response = ask_groq(prompt)
    if not response:
        await update.message.reply_text("Помилка при обробці відповіді ШІ.")
        return

    await update.message.reply_text(response)