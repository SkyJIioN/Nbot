from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 Введіть монети для аналізу через кому (наприклад: BTC, ETH, SOL):"
    )

async def handle_coin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    symbols = [s.strip().upper() for s in text.split(",") if s.strip()]
    timeframe = "1h"
    messages = []

    for symbol in symbols:
        try:
            result = await analyze_crypto(symbol, timeframe)
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка під час аналізу {symbol}: {e}")
            continue

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

        try:
            llm_response = await generate_signal_description(
                symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                bb_upper, bb_lower, trend, support, resistance
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка від LLM для {symbol}: {e}")
            continue

        if "LONG" in llm_response or "SHORT" in llm_response:
            msg = (
                f"📊 Аналіз {symbol} ({timeframe.upper()}):\n"
                f"{llm_response}\n"
                f"💱 Поточна ціна: {current_price:.2f}$"
            )
            messages.append(msg)

    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед заданих монет.")