from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from services.market_data import analyze_symbol
from services.groq_client import ask_groq


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть символ монети, наприклад BTC або ETH (латиницею):")


async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()

    await update.message.reply_text(f"⏳ Аналізую {symbol} на таймфреймі 4 години...")

    result = analyze_symbol(symbol)
    if isinstance(result, str):
        await update.message.reply_text(f"⚠️ {result}")
        return

    indicators_str, entry_price, rsi, sma = result

    prompt = (
        f"Проаналізуй криптовалюту {symbol} на 4H таймфреймі.\n"
        f"Поточна ціна: ${entry_price:.2f}\n"
        f"RSI: {rsi:.2f}, SMA: {sma:.2f}\n"
        f"Зроби короткий технічний аналіз і дай рекомендацію:\n"
        f"- чи варто відкривати long чи short\n"
        f"- вкажи орієнтовні точки входу/виходу у форматі USD\n"
        f"- не перевищуй 3 речення, українською мовою."
    )

    try:
        response = ask_groq(prompt)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка від Groq: {e}")


def get_handlers():
    return [
        CommandHandler("analyze", analyze_command),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_input)
    ]