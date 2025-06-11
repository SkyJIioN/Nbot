from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import get_historical_prices
from services.plotting import plot_price_chart

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = "BTC"  # можна зробити кнопки для вибору
    try:
        df = get_historical_prices(symbol)
        image_buf = plot_price_chart(df, symbol)

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=image_buf,
            caption=f"Ось графік ціни {symbol.upper()} за останній день 📈"
        )
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")
