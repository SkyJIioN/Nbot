import logging
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from services.market_data import get_crypto_prices
from services.groq_client import ask_groq
import telegram

# --- Telegram ---
from config import TELEGRAM_TOKEN

app = FastAPI()
app_telegram = Application.builder().token(TELEGRAM_TOKEN).build()

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Команди ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Аналіз BTC та ETH", callback_data="analyze")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привіт! Обери дію:", reply_markup=reply_markup)

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Якщо це callback
        if update.callback_query:
            await update.callback_query.answer()
            chat_id = update.callback_query.message.chat.id
            await context.bot.send_message(chat_id, "⏳ Очікую дані...")
        else:
            chat_id = update.message.chat.id
            await context.bot.send_message(chat_id, "⏳ Очікую дані...")

        prices = get_crypto_prices()  # {'bitcoin': 67000.0, 'ethereum': 3200.0}
        logger.info(f"Ціни: {prices}")

        prompt = (
            f"Поточна ціна BTC: ${prices['bitcoin']}, ETH: ${prices['ethereum']}.\n"
            "Чи варто входити в позицію на 1H графіку?\n"
            "Дай коротку відповідь (до 3 речень), аргументуй технічно. Відповідай українською."
        )

        response = ask_groq(prompt)

        message = (
            f"📊 Аналіз ринку:\n"
            f"BTC: ${prices['bitcoin']}\nETH: ${prices['ethereum']}\n\n"
            f"{response}"
        )

        await context.bot.send_message(chat_id=chat_id, text=message)

    except Exception as e:
        logger.error(f"Помилка в analyze: {e}")
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Помилка під час аналізу.")

# --- FastAPI маршрут для webhook ---
@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        print(f"⚡ Отримано оновлення: {data}")
        update = Update.de_json(data, app_telegram.bot)
        await app_telegram.process_update(update)
    except Exception as e:
        import traceback
        print("❌ ПОМИЛКА В ОБРОБЦІ UPDATE:")
        traceback.print_exc()
    return {"status": "ok"}

# --- Реєстрація обробників ---
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", analyze))