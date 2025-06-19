from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.market_data import analyze_symbol

# Зберігати символ тимчасово для кожного користувача
user_state = {}

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✏️ Введіть символ монети (наприклад, BTC, ETH, SOL):"
    )

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    user_state[update.effective_chat.id] = {"symbol": symbol}

    keyboard = [
        [InlineKeyboardButton("1H", callback_data="tf_1h"),
         InlineKeyboardButton("4H", callback_data="tf_4h"),
         InlineKeyboardButton("12H", callback_data="tf_12h")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⏱️ Виберіть таймфрейм:", reply_markup=reply_markup)

async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    if chat_id not in user_state:
        await query.edit_message_text("⚠️ Спочатку введіть символ монети.")
        return

    symbol = user_state[chat_id]["symbol"]
    timeframe = query.data.replace("tf_", "").lower()

    await query.edit_message_text(f"🔍 Аналіз {symbol} на таймфреймі {timeframe.upper()}...")

    try:
        result = analyze_symbol(symbol, interval=timeframe)

        if not result:
            await query.message.reply_text(f"⚠️ Не вдалося отримати дані для {symbol}.")
            return

        indicators_str = (
            f"Ціна: {result['price']}\n"
            f"RSI: {result['rsi']}\n"
            f"EMA20: {result['ema20']}, EMA50: {result['ema50']}\n"
            f"MACD: {result['macd']} / {result['macd_signal']}\n"
            f"Bollinger Bands: {result['lower_band']} - {result['upper_band']}\n"
            f"ATR: {result['atr']}\n"
        )

        signal_text = f"\nРекомендація: {result['signal']}"
        if result.get("reason"):
            signal_text += f"\nПричина: {result['reason']}"

        await query.message.reply_text(
            f"📊 Аналіз {symbol} ({timeframe.upper()}):\n\n"
            f"{indicators_str}"
            f"{signal_text}"
        )

    except Exception as e:
        await query.message.reply_text(f"❌ Помилка аналізу: {e}")
        print(f"Error during timeframe handling: {e}")