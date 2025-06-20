async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    timeframe = query.data.replace("tf_", "")
    symbol = context.user_data.get("symbol")

    await query.edit_message_text(f"⏳ Аналізую {symbol} на таймфреймі {timeframe.upper()}...")

    try:
        result = analyze_crypto(symbol, timeframe)  # ⬅️ без await

        if result is None:
            await query.message.reply_text(f"❌ Не вдалося отримати дані для {symbol}")
            return

        indicators_str, entry_price, exit_price, rsi, sma = result

        response = (
            f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
            f"{indicators_str}\n"
            f"💰 Потенційна точка входу: {entry_price:.2f}$\n"
            f"📈 Ціль для виходу: {exit_price:.2f}$\n"
            f"🔁 RSI: {rsi:.2f}\n"
            f"📊 SMA: {sma:.2f}"
        )
        await query.message.reply_text(response)

    except Exception as e:
        await query.message.reply_text(f"❌ Помилка при аналізі: {e}")