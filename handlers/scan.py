# scan.py

from telegram import Update
from telegram.ext import ContextTypes
from services.market_data import analyze_crypto
from services.llm_analysis import generate_signal_description

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # ⌛️ Старт
        await update.message.reply_text("🔍 Введіть символи монет через кому (наприклад: BTC, ETH, SOL):")
        return

    except Exception as e:
        print(f"❌ Помилка в scan_command: {e}")
        await update.message.reply_text("❌ Виникла помилка під час запуску команди.")