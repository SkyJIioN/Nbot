from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description


# Крок 1: Обробка команди /scan
async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "🔍 Введіть символи монет через кому (наприклад: BTC, ETH, SOL):"
        )
    except Exception as e:
        print(f"❌ Помилка в scan_command: {e}")
        await update.message.reply_text("❌ Виникла помилка при запуску сканування.")


# Крок 2: Обробка монет, введених користувачем
async def handle_scan_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text
        symbols = [s.strip().upper() for s in user_input.split(",")]
        timeframe = "1h"
        messages = []

        for symbol in symbols:
            try:
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
                    resistance,
                    price,
                ) = result

                try:
                    llm_response = await generate_signal_description(
                        symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                        bb_upper, bb_lower, trend, support, resistance, price
                    )

                    print(f"🔁 Відповідь LLM для {symbol}:\n{llm_response}")
                except Exception as e:
                    print(f"❌ Помилка під час генерації сигналу для {symbol}: {e}")
                    continue

                if "LONG" in llm_response or "SHORT" in llm_response:
                    message = (
                        f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
                        f"{llm_response}\n"
                        f"💱 Поточна ціна: {float(price):.5f}$\n"
                        f"🔁 RSI: {rsi:.2f}\n"
                        f"📊 SMA: {sma:.2f}\n"
                        f"📉 EMA: {ema:.2f}\n"
                        f"📊 MACD: {macd:.2f}, Сигнальна: {macd_signal:.2f}\n"
                        f"📊 Bollinger Bands: Верхня {bb_upper:.2f}$ / Нижня {bb_lower:.2f}$\n"
                        f"📉 Тренд: {trend.capitalize()}\n"
                        f"🔻 Підтримка: {support:.2f}$, 🔺 Опір: {resistance:.2f}$"
                    )
                    messages.append(message)

            except Exception as e:
                await update.message.reply_text(f"❌ Помилка під час аналізу {symbol}: {e}")
                continue

        if messages:
            for msg in messages:
                await update.message.reply_text(msg)
        else:
            await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед вказаних монет.")

    except Exception as e:
        print(f"❌ Помилка в handle_scan_input: {e}")
        await update.message.reply_text("❌ Виникла помилка при обробці монет.")