from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

# Тимчасовий список монет (замість фіксованого)
MONETS = ["AKT", "BTC", "ETH", "SOL", "APT", "BCH", "XRP"]

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframe = "1h"
    messages = []

    for symbol in MONETS:
        try:
            result = await analyze_crypto(symbol, timeframe)
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

            # Виклик LLM
            llm_response = await generate_signal_description(
                symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                trend, support, resistance, price
            )

            if "LONG" in llm_response or "SHORT" in llm_response:
                response = (
                    f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
                    f"{llm_response}\n"
                    f"💱 Поточна ціна: {float(current_price):.2f}$\n"
                    f"📉 Тренд: {trend.capitalize()}\n"
                    f"🔻 Лінія підтримки: {float(support):.2f}$\n"
                    f"🔺 Лінія опору: {float(resistance):.2f}$\n"
                    f"💰 Точка входу: {float(entry_price):.2f}$\n"
                    f"📈 Точка виходу: {float(exit_price):.2f}$\n"
                    f"🔁 RSI: {float(rsi):.2f}\n"
                    f"📊 SMA: {float(sma):.2f}\n"
                    f"📉 EMA: {float(ema):.2f}\n"
                    f"📊 MACD: {float(macd):.2f}, Сигнальна: {float(macd_signal):.2f}\n"
                    f"📊 Bollinger Bands: Верхня {float(bb_upper):.2f}$ / Нижня {float(bb_lower):.2f}$"
                )
                messages.append(response)

        except Exception as e:
            await update.message.reply_text(f"❌ Помилка під час аналізу {symbol}: {e}")

    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед заданих монет.")