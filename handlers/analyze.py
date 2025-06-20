# handlers/analyze.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.market_data import analyze_symbol 

# Зберігаємо символ монети, щоб потім отримати його після вибору таймфрейму
user_context = {}

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть символ криптовалюти (наприклад: BTC, ETH):")

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    user_id = update.effective_user.id
    user_context[user_id] = {"symbol": symbol}

    keyboard = [
        [
            InlineKeyboardButton("1H", callback_data="tf_1h"),
            InlineKeyboardButton("4H", callback_data="tf_4h"),
            InlineKeyboardButton("12H", callback_data="tf_12h"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Виберіть таймфрейм для аналізу {symbol}:", reply_markup=reply_markup)

async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    symbol_data = user_context.get(user_id)

    if not symbol_data:
        await query.edit_message_text("⚠️ Не вдалося знайти символ монети. Спробуйте /analyze знову.")
        return

    symbol = symbol_data["symbol"]
    timeframe = query.data.replace("tf_", "")

    await query.edit_message_text(f"⏳ Аналізую {symbol} на таймфреймі {timeframe.upper()}...")

    try:
        result = await analyze_crypto(symbol, timeframe)
        if result:
            await query.message.reply_text(result)
        else:
            await query.message.reply_text(f"⚠️ Не вдалося отримати дані для {symbol.upper()}.")
    except Exception as e:
        await query.message.reply_text(f"❌ Помилка при аналізі: {e}")