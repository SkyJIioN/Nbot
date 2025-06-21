from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.market_data import analyze_crypto, get_current_price

# Список доступних таймфреймів
TIMEFRAMES = {
    "1H": "1h",
    "4H": "4h",
    "12H": "12h"
}

# Крок 1: Команда /analyze
async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Введіть символ монети для аналізу (наприклад, BTC, ETH, SOL):")

# Крок 2: Ввід монети
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

# Крок 3: Обробка вибору таймфрейму
async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    timeframe = query.data.replace("tf_", "")
    symbol = context.user_data.get("symbol")

    await query.edit_message_text(f"⏳ Аналізую {symbol} на таймфреймі {timeframe.upper()}...")

    try:
        result = await analyze_crypto(symbol, timeframe)

        if result is None:
            await query.message.reply_text("⚠️ Недостатньо даних для аналізу.")
            return

        indicators_str, entry_price, exit_price, rsi, sma = result

        # Отримати поточну ціну
        current_price = get_current_price(symbol)
        if current_price is None:
            current_price_text = "❌ Поточну ціну не вдалося отримати."
        else:
            current_price_text = f"💱 Поточна ціна: {current_price:.5f}$"

        response = (
            f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
            f"{indicators_str}\n"
            f"{current_price_text}\n"
            f"💰 Потенційна точка входу: {entry_price:.5f}$\n"
            f"📈 Ціль для виходу: {exit_price:.5f}$\n"
            f"🔁 RSI: {rsi:.5f}\n"
            f"📊 SMA: {sma:.5f}"
        )

        await query.message.reply_text(response)

    except Exception as e:
        await query.message.reply_text(f"❌ Помилка при аналізі: {e}")