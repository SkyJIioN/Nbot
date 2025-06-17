from telegram import Update 
from telegram.ext import ContextTypes

from services.market_data import get_analysis_for_symbol

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Введіть символ монети (наприклад, BTC або ETH), щоб отримати аналіз.")

async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE): symbol = update.message.text.strip().upper() await update.message.reply_text(f"Аналізую {symbol} на таймфреймі 4 години...")

result = await get_analysis_for_symbol(symbol)
if isinstance(result, str):
    await update.message.reply_text(result)
    return

rsi = result['rsi']
sma = result['sma']
current_price = result['current_price']

signal = ""
entry = current_price
take_profit = None
stop_loss = None

if rsi < 30 and current_price > sma:
    signal = "LONG 📈"
    take_profit = round(entry * 1.03, 2)
    stop_loss = round(entry * 0.97, 2)
elif rsi > 70 and current_price < sma:
    signal = "SHORT 📉"
    take_profit = round(entry * 0.97, 2)
    stop_loss = round(entry * 1.03, 2)
else:
    signal = "Немає чіткого сигналу. 📊"

response = (
    f"Монета: {symbol}" 
f"Ціна: ${current_price}" 
f"RSI: {rsi} | SMA: {sma}" 
f"Рекомендація: {signal}" )

if take_profit and stop_loss:
    response += f"\nТочка входу: ${entry}\nTake Profit: ${take_profit}\nStop Loss: ${stop_loss}"

await update.message.reply_text(response)

