from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description


async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        symbols = [s.strip().upper() for s in " ".join(context.args).replace(",", " ").split()]
    else:
        await update.message.reply_text("🔎 Введіть монети для аналізу, наприклад: /scan BTC ETH SOL")
        return

    messages = []

    for symbol in symbols:
        try:
            result = await analyze_crypto(symbol, "1h")
            if not result:
                messages.append(f"⚠️ Недостатньо даних для {symbol}")
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

            llm_response = await generate_signal_description(
                symbol, "1h", rsi, sma, ema, macd, macd_signal,
                bb_upper, bb_lower, trend, support, resistance, current_price
            )

            if "LONG" in llm_response or "SHORT" in llm_response:
                msg = (
                    f"📊 Аналіз {symbol} (1H):\n"
                    f"{llm_response}\n"
                    f"💱 Поточна ціна: {float(current_price):.5f}$\n"
                    f"🔁 RSI: {rsi:.2f}\n"
                    f"📊 SMA: {sma:.2f}\n"
                    f"📉 EMA: {ema:.2f}\n"
                    f"📊 MACD: {macd:.2f}, Сигнальна: {macd_signal:.2f}\n"
                    f"📊 Bollinger Bands: Верхня {bb_upper:.2f}$ / Нижня {bb_lower:.2f}$\n"
                    f"📉 Тренд: {trend.capitalize()}\n"
                    f"🔻 Підтримка: {support:.2f}$, 🔺 Опір: {resistance:.2f}$"
                )
                messages.append(msg)

        except Exception as e:
            messages.append(f"❌ Помилка при аналізі {symbol}: {e}")

    if messages:
        for m in messages:
            await update.message.reply_text(m)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед вказаних монет.")