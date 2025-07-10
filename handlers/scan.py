from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description


async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message_text = update.message.text
        if not message_text:
            await update.message.reply_text("⚠️ Не вдалося прочитати текст повідомлення.")
            return

        parts = message_text.strip().split(maxsplit=1)
        if len(parts) < 2:
            await update.message.reply_text("📝 Введіть символи монет через кому після команди /scan (наприклад: `/scan BTC, ETH, SOL`)", parse_mode="Markdown")
            return

        input_symbols = parts[1].replace(" ", "").split(",")
        timeframe = "1h"
        messages = []

        for symbol in input_symbols:
            try:
                print(f"🔍 Аналізую {symbol}...")
                result = analyze_crypto(symbol, timeframe)

                if not result:
                    await update.message.reply_text(f"⚠️ Недостатньо даних для {symbol}")
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
    bb_upper, bb_lower, trend, support, resistance, current_price
)

print(f"🔁 Відповідь LLM для {symbol}:\n{llm_response}")

                if not llm_response:
                    await update.message.reply_text(f"⚠️ LLM не повернув відповідь для {symbol}")
                    continue

                print(f"🔁 LLM відповідь для {symbol}:\n{llm_response}")

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
            except Exception as err:
                await update.message.reply_text(f"❌ Помилка під час аналізу {symbol}: {err}")

        if messages:
            for msg in messages:
                await update.message.reply_text(msg)
        else:
            await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед вказаних монет.")

    except Exception as main_error:
        await update.message.reply_text(f"❌ Загальна помилка: {main_error}")