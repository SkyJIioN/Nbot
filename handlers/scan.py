# handlers/scan.py
from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

# Список монет (можна змінювати)
MONETS = ["BTC", "ETH", "SOL", "XRP", "BCH"]

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframe = "1h"
    messages = []

    for symbol in MONETS:
        try:
            result = analyze_crypto(symbol, timeframe)
            if not result:
                continue

            (
                _indicators_str,
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

            # LLM-аналітика
            llm_response = await generate_signal_description(
                symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                bb_upper, bb_lower, trend, support, resistance
            )

            # Якщо є чіткий сигнал, надсилаємо
            if "LONG" in llm_response.upper() or "SHORT" in llm_response.upper():
                msg = f"📊 Аналіз {symbol} ({timeframe.upper()}):\n{llm_response}"
                messages.append(msg)

        except Exception as e:
            await update.message.reply_text(f"❌ Помилка під час аналізу {symbol}: {e}")

    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед заданих монет.")