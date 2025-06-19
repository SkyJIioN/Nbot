from telegram import Update
from telegram.ext import ContextTypes

from services.market_data import analyze_symbol


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✏️ Введіть символ монети (наприклад, BTC, ETH, SOL), яку ви хочете проаналізувати:"
    )


async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    await update.message.reply_text(f"⏳ Аналізую {symbol} на таймфреймі 4H...")

    try:
        result = analyze_symbol(symbol)
        if not result:
            await update.message.reply_text(f"⚠️ Не вдалося отримати дані для {symbol}.")
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

        await update.message.reply_text(
            f"📊 Аналіз {symbol} на 4H:\n\n"
            f"{indicators_str}"
            f"{signal_text}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Помилка аналізу: {e}")
        print(f"Error in analyze handler: {e}")