from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.market_data import analyze_symbol

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введіть символ криптовалюти, наприклад: BTC або ETH"
    )

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    context.user_data["symbol"] = symbol

    keyboard = [
        [InlineKeyboardButton("1H", callback_data="tf_1h"),
         InlineKeyboardButton("4H", callback_data="tf_4h"),
         InlineKeyboardButton("12H", callback_data="tf_12h")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Оберіть таймфрейм для аналізу {symbol}:",
        reply_markup=reply_markup
    )

async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    symbol = context.user_data.get("symbol", "BTC")
    timeframe = query.data.replace("tf_", "")

    await query.edit_message_text(f"Аналізую {symbol} на таймфреймі {timeframe.upper()}...")

    data = analyze_symbol(symbol, interval=timeframe)
    if data is None:
        await query.message.reply_text("⚠️ Не вдалося отримати дані.")
        return

    text = (
        f"💹 *{symbol.upper()}* ({timeframe})\n"
        f"Ціна: *{data['price']} USD*\n"
        f"RSI: {data['rsi']}\n"
        f"EMA20: {data['ema20']}\n"
        f"EMA50: {data['ema50']}\n"
        f"MACD: {data['macd']} | Signal: {data['macd_signal']}\n"
        f"ATR: {data['atr']}\n"
        f"📊 Рекомендація: *{data['signal']}*\n"
        f"Причина: _{data['reason']}_"
    )
    await query.message.reply_text(text, parse_mode="Markdown")