from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import get_ohlcv_data
from services.ta import analyze_market
from services.groq_client import ask_groq


async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    await update.message.reply_text(f"Аналізую {symbol} на таймфреймі 4 години...")

    try:
        ohlcv = get_ohlcv_data(symbol)
        if not ohlcv:
            await update.message.reply_text("Не вдалося отримати ринкові дані.")
            return

        ta_summary = analyze_market(ohlcv)
        prompt = (
            f"На основі цих технічних індикаторів:\n{ta_summary}\n\n"
            f"Визнач точку входу, виходу та напрямок угоди (Long або Short) для {symbol} "
            f"на таймфреймі 4 години. Відповідь українською, стисло."
        )

        groq_response = ask_groq(prompt)
        await update.message.reply_text(groq_response)

    except Exception as e:
        await update.message.reply_text("Виникла помилка під час аналізу.")
        print("Error in handle_symbol_input:", e)