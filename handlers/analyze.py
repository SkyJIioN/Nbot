# handlers/analyze.py
from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_symbol

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