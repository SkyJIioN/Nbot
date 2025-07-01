# handlers/scan.py
from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

# Фіксований список монет
MONETS = ["BTC", "ETH", "SOL", "APT", "BCH", "XRP"]

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframe = "1h"
    messages = []

    for symbol in MONETS:
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
            bb_upper, bb_lower, trend, support, resistance
        )

        if "LONG" in llm_response or "SHORT" in llm_response:
            response = (
                f"\U0001F4CA Аналіз {symbol} ({timeframe.upper()}):\n"
                f"{llm_response}\n"
                f"\U0001F4B1 Поточна ціна: {current_price:.2f}$\n"
                f"\U0001F4C9 Тренд: {trend.capitalize()}\n"
                f"\U0001F53B Лінія підтримки: {support:.2f}$\n"
                f"\U0001F53A Лінія опору: {resistance:.2f}$\n"
                f"\U0001F4B0 Точка входу: {entry_price:.2f}$\n"
                f"\U0001F4C8 Точка виходу: {exit_price:.2f}$\n"
                f"\U0001F501 RSI: {rsi:.2f}\n"
                f"\U0001F4CA SMA: {sma:.2f}\n"
                f"\U0001F4C9 EMA: {ema:.2f}\n"
                f"\U0001F4CA MACD: {macd:.2f}, Сигнальна: {macd_signal:.2f}\n"
                f"\U0001F4CA Bollinger Bands: Верхня {bb_upper:.2f}$ / Нижня {bb_lower:.2f}$"
            )
            messages.append(response)

    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("\u26A0\uFE0F Немає чітких сигналів (LONG або SHORT) серед заданих монет.")