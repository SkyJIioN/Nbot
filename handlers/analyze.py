from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import get_indicators
from services.groq_client import ask_groq

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()

    await update.message.reply_text(f"Аналізую {symbol} на таймфреймі 4 години...")

    indicators = get_indicators(symbol)
    if not indicators:
        await update.message.reply_text("Не вдалося отримати дані для аналізу.")
        return

    prompt = (
        f"Проаналізуй криптовалюту {symbol} на основі наступних технічних індикаторів:\n"
        f"- Поточна ціна: {indicators['current_price']} USD\n"
        f"- SMA (14): {indicators['SMA_14']} USD\n"
        f"- RSI (14): {indicators['RSI_14']}\n\n"
        f"Оціни тренд, напиши короткий технічний аналіз українською мовою, "
        f"зазнач чи відкривати позицію LONG чи SHORT, та вкажи орієнтовні точки входу та виходу."
    )

    try:
        analysis = await ask_groq(prompt)
        await update.message.reply_text(analysis)
    except Exception as e:
        print("Groq error:", e)
        await update.message.reply_text("Виникла помилка під час отримання аналітики.")