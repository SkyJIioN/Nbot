from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.market_data import analyze_crypto

TIMEFRAMES = {
    "1H": "1h",
    "4H": "4h",
    "12H": "12h"
}

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Введіть символ монети для аналізу (наприклад, BTC, ETH, SOL):")

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    context.user_data["symbol"] = symbol

    keyboard = [
        [InlineKeyboardButton(tf, callback_data=f"tf_{TIMEFRAMES[tf]}")]
        for tf in TIMEFRAMES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📈 Оберіть таймфрейм для {symbol}:",
        reply_markup=reply_markup
    )

async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    timeframe = query.data.replace("tf_", "")
    symbol = context.user_data.get("symbol")

    await query.edit_message_text(f"⏳ Аналізую {symbol} на таймфреймі {timeframe.upper()}...")

    try:
        indicators_str, entry_price, exit_price, rsi, sma = await analyze_crypto(symbol, timeframe)

        response = (
            f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
            f"{indicators_str}\n"
            f"💰 Вхід: {entry_price:.2f}$\n"
            f"📈 Вихід: {exit_price:.2f}$\n"
            f"🔁 RSI: {rsi:.2f}\n"
            f"📊 SMA: {sma:.2f}"
        )
        await query.message.reply_text(response)

    except Exception as e:
        await query.message.reply_text(f"❌ Помилка при аналізі: {e}")