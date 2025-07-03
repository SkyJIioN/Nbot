from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframe = "1h"
    messages = []

    # 🧾 Якщо користувач не передав монети
    if not context.args:
        await update.message.reply_text(
            "🔎 Введіть монети для аналізу через пробіл або кому:\n"
            "Приклад: /scan BTC ETH SOL або /scan BTC,ETH"
        )
        return

    # 🔍 Обробка вводу монет (через пробіл або кому)
    raw_input = " ".join(context.args)
    if "," in raw_input:
        symbols = [s.strip().upper() for s in raw_input.split(",") if s.strip()]
    else:
        symbols = [s.strip().upper() for s in raw_input.split(" ") if s.strip()]

    for symbol in symbols:
        result = analyze_crypto(symbol, timeframe)
        if not result:
            continue

        try:
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

        except Exception as e:
            await update.message.reply_text(f"❌ Помилка під час аналізу {symbol}: {e}")

    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед заданих монет.")