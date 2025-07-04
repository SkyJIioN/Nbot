from telegram import Update
from telegram.ext import ContextTypes

from services.market_data import get_crypto_price
from services.groq_client import ask_groq
from handlers.analyze import analyze_handler
application.add_handler(analyze_handler)

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть символ монети, наприклад BTC або ETH.")

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()

    try:
        df = fetch_historical_prices(symbol, COINMARKETCAP_API_KEY)
        analysis = analyze_technical(df)

        message = (
            f"🔍 Аналіз для {symbol}:\n"
            f"📈 Поточна ціна: ${analysis['price']}\n"
            f"📊 SMA(14): ${analysis['SMA']}\n"
            f"💹 RSI: {analysis['RSI']:.2f}\n"
            f"📌 Рекомендація: {analysis['recommendation']}"
        )
    except Exception as e:
        message = f"❌ Не вдалося отримати дані по {symbol}. Помилка: {e}"

    await update.message.reply_text(message)