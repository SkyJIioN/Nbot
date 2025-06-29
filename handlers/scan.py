from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

# 👉 Монети, які будемо сканувати
SYMBOLS = ["BTC", "ETH", "SOL", "APT", "BCH", "XRP", "LTC", "LINK"]
TIMEFRAME = "1h"

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Сканую монети з таймфреймом 1H. Це займе кілька секунд...")

    results = []
    for symbol in SYMBOLS:
        try:
            result = analyze_crypto(symbol, TIMEFRAME)
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
                support_level,
                resistance_level
            ) = result

            llm_response = await generate_signal_description(
                symbol, TIMEFRAME, rsi, sma, ema, macd, macd_signal, trend
            )

            # 🎯 Фільтруємо лише сигнали LONG або SHORT
            if "LONG" in llm_response.upper() or "SHORT" in llm_response.upper():
                results.append(f"📊 {symbol}:\n{llm_response}\n💱 Ціна: {current_price:.2f}$\n")

        except Exception as e:
            print(f"Помилка для {symbol}: {e}")
            continue

    if results:
        reply = "✅ Монети з чіткими сигналами:\n\n" + "\n".join(results)
    else:
        reply = "⚠️ Немає чітких сигналів (LONG або SHORT) серед заданих монет."

    await update.message.reply_text(reply)