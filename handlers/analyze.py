# analyze.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

TIMEFRAMES = {
    "1H": "1h",
    "4H": "4h",
    "12H": "12h"
}

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\ud83d\udd0e \u0412\u0432\u0435\u0434\u0456\u0442\u044c \u0441\u0438\u043c\u0432\u043e\u043b \u043c\u043e\u043d\u0435\u0442\u0438 \u0434\u043b\u044f \u0430\u043d\u0430\u043b\u0456\u0437\u0443 (\u043d\u0430\u043f\u0440\u0438\u043a\u043b\u0430\u0434, BTC, ETH, SOL):")

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    context.user_data["symbol"] = symbol

    keyboard = [
        [InlineKeyboardButton(tf, callback_data=f"tf_{TIMEFRAMES[tf]}")]
        for tf in TIMEFRAMES
    ]
    await update.message.reply_text(
        f"\ud83d\udcc8 \u041e\u0431\u0435\u0440\u0456\u0442\u044c \u0442\u0430\u0439\u043c\u0444\u0440\u0435\u0439\u043c \u0434\u043b\u044f {symbol}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    timeframe = query.data.replace("tf_", "")
    symbol = context.user_data.get("symbol")
    await query.edit_message_text(f"\u23f3 \u0410\u043d\u0430\u043b\u0456\u0437\u0443\u044e {symbol} \u043d\u0430 \u0442\u0430\u0439\u043c\u0444\u0440\u0435\u0439\u043c\u0456 {timeframe.upper()}...")

    try:
        result = analyze_crypto(symbol, timeframe)

        if not result:
            await query.message.reply_text("\u26a0\ufe0f \u041d\u0435\u0434\u043e\u0441\u0442\u0430\u0442\u043d\u044c\u043e \u0434\u0430\u043d\u0438\u0445 \u0434\u043b\u044f \u0430\u043d\u0430\u043b\u0456\u0437\u0443.")
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

        llm_response = await generate_signal_description(
            symbol, timeframe, rsi, sma, ema, macd, macd_signal
        )

        response = (
            f"\ud83d\udcca \u0410\u043d\u0430\u043b\u0456\u0437 {symbol} ({timeframe.upper()}):\n"
            f"{llm_response}\n"
            f"\ud83d\udcb1 \u041f\u043e\u0442\u043e\u0447\u043d\u0430 \u0446\u0456\u043d\u0430: {current_price:.2f}$\n"
            f"\ud83d\udcb0 \u041f\u043e\u0442\u0435\u043d\u0446\u0456\u0439\u043d\u0430 \u0442\u043e\u0447\u043a\u0430 \u0432\u0445\u043e\u0434\u0443: {entry_price:.2f}$\n"
            f"\ud83d\udcc8 \u0426\u0456\u043b\u044c \u0434\u043b\u044f \u0432\u0438\u0445\u043e\u0434\u0443: {exit_price:.2f}$\n"
            f"\ud83d\udd01 RSI: {rsi:.2f}\n"
            f"\ud83d\udccb SMA: {sma:.2f}\n"
            f"\ud83d\udcc9 EMA: {ema:.2f}\n"
            f"\ud83d\udccb MACD: {macd:.2f}, \u0421\u0438\u0433\u043d\u0430\u043b\u044c\u043d\u0430: {macd_signal:.2f}\n"
            f"\ud83d\udccb Bollinger Bands: \u0412\u0435\u0440\u0445\u043d\u044f {bb_upper:.2f}$ / \u041d\u0438\u0436\u043d\u044f {bb_lower:.2f}$"
        )

        await query.message.reply_text(response)

    except Exception as e:
        await query.message.reply_text(f"\u274c \u041f\u043e\u043c\u0438\u043b\u043a\u0430 \u043f\u0440\u0438 \u0430\u043d\u0430\u043b\u0456\u0437\u0456: {e}")