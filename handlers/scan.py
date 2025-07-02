# handlers/scan.py
from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframe = "1h"

    # Якщо користувач не передав монети
    if not context.args:
        await update.message.reply_text("🔎 Введіть символи монет через кому або пробіл: /scan BTC, ETH або /scan BTC ETH")
        return

    # Розбір монет
    raw_input = " ".join(context.args)
    separators = [",", " "]
    for sep in separators:
        if sep in raw_input:
            monets = [x.strip().upper() for x in raw_input.split(sep) if x.strip()]
            break
    else:
        monets = [raw_input.strip().upper()]

    messages = []

    for symbol in monets:
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
            trend, support, resistance
        )

        if "LONG" in llm_response or "SHORT" in llm_response:
            response = (
                f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
                f"{llm_response}\n"
                f"💱 Поточна ціна: {current_price:.2f}$"
            )
            messages.append(response)

    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед заданих монет.")