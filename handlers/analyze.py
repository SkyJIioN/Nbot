from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

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
    await update.message.reply_text(
        f"📈 Оберіть таймфрейм для {symbol}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Крок 3: Обробка вибору таймфрейму
async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    timeframe = query.data.replace("tf_", "")
    symbol = context.user_data.get("symbol")
    await query.edit_message_text(f"⏳ Аналізую {symbol} на таймфреймі {timeframe.upper()}...")

    try:
        result = analyze_crypto(symbol, timeframe)  # <- без await

        if not result:
            await query.message.reply_text("⚠️ Недостатньо даних для аналізу.")
            return
    (
    indicators_str,
    current_price,
    entry_price,
    exit_price,
    rsi,
    sma,
    ema,
    macd,
    macd_signal,
    bb_upper,
    bb_lower
) = result
) = result

        llm_response = generate_signal_description(
            symbol, timeframe, rsi, sma, ema, macd, macd_signal
        )

        response = (
            f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
            f"{llm_response}\n"
            f"💱 Поточна ціна: {current_price:.2f}$\n"
            f"💰 Потенційна точка входу: {entry_price:.2f}$\n"
            f"📈 Ціль для виходу: {exit_price:.2f}$\n"
            f"🔁 RSI: {rsi:.2f}\n"
            f"📊 SMA: {sma:.2f}\n"
            f"📉 EMA: {ema:.2f}\n"
            f"📊 MACD: {macd:.2f}, Сигнальна: {macd_signal:.2f}"
        )
        await query.message.reply_text(response)

    except Exception as e:
        await query.message.reply_text(f"❌ Помилка при аналізі: {e}")