from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframe = "1h"
    messages = []

    # Отримуємо монети з тексту команди
    if context.args:
        input_text = " ".join(context.args)
        symbols = [s.strip().upper() for s in input_text.replace(",", " ").split()]
    else:
        await update.message.reply_text("🔎 Введіть монети для аналізу, наприклад: `/scan BTC, ETH, SOL`", parse_mode="Markdown")
        return

    for symbol in symbols:
        try:
            result = analyze_crypto(symbol, timeframe)
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

            llm_response = await generate_signal_description(
    symbol, timeframe, rsi, sma, ema, macd, macd_signal,
    trend, support, resistance,
    bb_upper, bb_lower, current_price
)

            if "LONG" in llm_response or "SHORT" in llm_response:
                response = (
                    f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
                    f"{llm_response}\n"
                    f"💱 Поточна ціна: {current_price:.2f}$\n"
                    f"📉 Тренд: {trend.capitalize()}\n"
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
                messages.append(response)
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка під час аналізу {symbol}: {e}")

    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед введених монет.")