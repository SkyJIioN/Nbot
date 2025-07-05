from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframe = "15m"

    # Отримуємо текст після команди /scan
    text = update.message.text.replace("/scan", "").strip()

    if not text:
        await update.message.reply_text("🔎 Введіть монети через кому, наприклад:\n`/scan BTC, ETH, SOL`", parse_mode="Markdown")
        return

    # Розбиваємо введений текст у список монет
    symbols = [s.strip().upper() for s in text.split(",") if s.strip()]
    messages = []

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
                resistance,
                price
            ) = result

            llm_response = await generate_signal_description(
                symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                bb_upper, bb_lower, trend, support, resistance, price
            )

            if "LONG" in llm_response or "SHORT" in llm_response:
                response = (
                    f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
                    f"{llm_response}\n"
                    f"💱 Поточна ціна: {current_price:.5f}$\n"
                    f"🔁 RSI: {rsi:.5f}\n"
                    f"📊 SMA: {sma:.5f}\n"
                    f"📉 EMA: {ema:.5f}\n"
                    f"📊 MACD: {macd:.5f}, Сигнальна: {macd_signal:.5f}\n"
                    f"📊 Bollinger Bands: Верхня {bb_upper:.5f}$ / Нижня {bb_lower:.5f}$\n"
                    f"📉 Тренд: {trend.capitalize()}\n"
                    f"🔻 Підтримка: {support:.5f}$, 🔺 Опір: {resistance:.5f}$"
                )
                messages.append(response)

        except Exception as e:
            await update.message.reply_text(f"❌ Помилка під час аналізу {symbol}: {e}")

    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед введених монет.")