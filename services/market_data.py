import requests
from config import BINANCE_BASE_URL

def get_crypto_prices():
    symbols = ["BTCUSDT", "ETHUSDT"]
    prices = {}
    for symbol in symbols:
        url = f"{BINANCE_BASE_URL}/api/v3/ticker/price?symbol={symbol}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            prices[symbol.lower()] = float(data['price'])
        except Exception as e:
            print(f"Error fetching {symbol} from Binance: {e}")
    return prices


# === services/groq_client.py ===
import requests
from config import GROQ_API_KEY

def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq API error: {e}")
        return "Вибач, виникла помилка при аналізі."


# === webhook.py ===
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from services.market_data import get_crypto_prices
from services.groq_client import ask_groq

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Аналізувати BTC/ETH", callback_data="analyze")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привіт! Обери монету для аналізу:", reply_markup=reply_markup)

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Очікую дані...")

    prices = get_crypto_prices()
    if not prices:
        await query.edit_message_text("Помилка при отриманні цін з Binance")
        return

    prompt = f"Зроби короткий аналіз BTC і ETH на основі поточних цін: BTC = {prices.get('btcusdt')} USD, ETH = {prices.get('ethusdt')} USD. Які точки входу/виходу?"
    answer = ask_groq(prompt)
    await query.edit_message_text(answer)

# Хендлери
start = CommandHandler("start", start)
analyze = CallbackQueryHandler(analyze, pattern="^analyze$")
