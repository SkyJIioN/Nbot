# scan.py
from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

# Список монет
MONETS = ["BTC", "ETH", "SOL", "APT", "BCH", "XRP"]

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframe = "1h"
    messages = []

    for symbol in MONETS:
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

            # Примусове приведення до float
            current_price = float(current_price)
            entry_price = float(entry_price)
            exit_price = float(exit_price)
            rsi = float(rsi)
            sma = float(sma)
            ema = float(ema)
            macd = float(macd)
            macd_signal = float(macd_signal)
            bb_upper = float(bb_upper)
            bb_lower = float(bb_lower)
            support = float(support)
            resistance = float(resistance)

            # Отримуємо відповідь від LLM
            llm_response = await generate_signal_description(
                symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                trend, support, resistance
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
            messages.append(f"❌ Помилка під час аналізу {symbol}: {e}")

    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед заданих монет.")