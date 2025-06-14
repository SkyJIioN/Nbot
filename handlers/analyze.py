from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import fetch_price
from services.groq_client import ask_groq

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть символ монети (наприклад, BTC):")

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()

    await update.message.reply_text("Отримую дані...")

    price = fetch_price(symbol)
    if not price:
        await update.message.reply_text("Не вдалося отримати ціну. Перевірте правильність символу.")
        return

    prompt = (
    f"Ціна {symbol}: {price:.2f} USD.\n"
    "На основі ціни, зроби короткий технічний аналіз.\n"
    "Визнач оптимальну позицію (LONG або SHORT), точку входу, стоп-лосс та точку виходу (тейк-профіт).\n"
    "Формат відповіді:\n"
    "- Позиція: LONG або SHORT\n"
    "- Точка входу: \n"
    "- Стоп-лосс: \n"
    "- Тейк-профіт: \n"
    "- Рекомендоване кредитне плече"
    "- Орієнтовний заробіток при ставці в 10$"
    "Відповідай лаконічно українською мовою."
)

    response = ask_groq(prompt)
    if response:
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Помилка аналізу через Groq.")