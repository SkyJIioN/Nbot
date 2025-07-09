from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

# Обробка команди /scan SYMBOL1 SYMBOL2 ...
async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframe = "1h"

    if not context.args:
        await update.message.reply_text("❗ Вкажіть монети для аналізу після команди /scan (наприклад, /scan BTC ETH SOL)")
        return

    symbols = [s.upper() for s in context.args]
    messages = []

    for symbol in symbols:
        try:
            result = await analyze_crypto(symbol, timeframe)
            if not result:
                await update.message.reply_text(f"⚠️ Недостатньо даних для {symbol}.")
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

            try:
                llm_response = generate_signal_description(
                    symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                    bb_upper, bb_lower, trend, support, resistance, current_price
                )
                print(f"🔁 LLM відповідь для {symbol}:\n{llm_response}")
            except Exception as e:
                print(f"❌ Помилка при генерації LLM відповіді для {symbol}: {e}")
                continue

            if "LONG" in llm_response or "SHORT" in llm_response:
                response = (
                    f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
                    f"{llm_response}\n"
                    f"💱 Поточна ціна: {current_price:.5f}$\n"
                    f"🔁 RSI: {rsi:.2f}\n"
                    f"📊 SMA: {sma:.2f}\n"
                    f"📉 EMA: {ema:.2f}\n"
                    f"📊 MACD: {macd:.2f}, Сигнальна: {macd_signal:.2f}\n"
                    f"📊 Bollinger Bands: Верхня {bb_upper:.2f}$ / Нижня {bb_lower:.2f}$\n"
                    f"📉 Тренд: {trend.capitalize()}\n"
                    f"🔻 Підтримка: {support:.2f}$, 🔺 Опір: {resistance:.2f}$"
                )
                messages.append(response)

        except Exception as e:
            await update.message.reply_text(f"❌ Помилка під час аналізу {symbol}: {e}")

    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед заданих монет.")