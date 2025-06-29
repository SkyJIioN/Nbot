from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

MONITOR_SYMBOLS = ["BTC", "ETH", "SOL", "APT", "BCH", "XRP", "MATIC"]
TIMEFRAME = "1h"

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Сканую монети... Це може зайняти кілька секунд.")

    results = []
    for symbol in MONITOR_SYMBOLS:
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
                support,
                resistance
            ) = result

            llm_response = await generate_signal_description(
                symbol, TIMEFRAME, rsi, sma, ema, macd, macd_signal, trend, support, resistance
            )

            # Перевіряємо наявність чіткого сигналу
            if "LONG" in llm_response.upper() or "SHORT" in llm_response.upper():
                results.append(
                    f"📊 Аналіз {symbol}:"
                    f"{llm_response}"
                    f"💱 Ціна: {current_price:.2f}$\n"
                    f"🔁 RSI: {rsi:.2f}, SMA: {sma:.2f}, EMA: {ema:.2f}\n"
                    f"📊 MACD: {macd:.2f}, Signal: {macd_signal:.2f}\n"
                    f"📉 Тренд: {trend}, Support: {support:.2f}$, Resistance: {resistance:.2f}$"
                )
        except Exception as e:
            print(f"❌ Помилка для {symbol}: {e}")

    if results:
        await update.message.reply_text("\n\n".join(results))
    else:
        await update.message.reply_text("⚠️ Немає чітких сигналів (LONG або SHORT) серед заданих монет.")