from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    symbols = [s.strip().replace('"', '').replace("'", '').upper() for s in text.split(",")]

    responses = []
    for symbol in symbols:
        result = analyze_crypto(symbol, "1h")
        if not result:
            continue

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
            bb_lower,
            trend,
            support,
            resistance
        ) = result

        llm_response = generate_signal_description(
            symbol, "1h", rsi, sma, ema, macd, macd_signal, trend, support, resistance
        )

        if "LONG" in llm_response or "SHORT" in llm_response:
            message = (
                f"📊 Аналіз {symbol} (1H):\n"
                f"{llm_response}\n"
                f"💱 Поточна ціна: {current_price:.2f}$\n"
                f"📉 Тренд: {trend}\n"
                f"🔻 Лінія підтримки: {support:.2f}$\n"
                f"🔺 Лінія опору: {resistance:.2f}$\n"
                f"💰 Точка входу: {entry_price:.2f}$\n"
                f"📈 Точка виходу: {exit_price:.2f}$\n"
                f"🔁 RSI: {rsi:.2f}\n"
                f"📊 SMA: {sma:.2f}\n"
                f"📉 EMA: {ema:.2f}\n"
                f"📊 MACD: {macd:.2f}, Сигнальна: {macd_signal:.2f}\n"
                f"📊 Bollinger Bands: Верхня {bb_upper:.2f}$ / Нижня {bb_lower:.2f}$"
            )
            responses.append(message)

    if responses:
        for msg in responses:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед заданих монет.")