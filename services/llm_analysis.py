import os
import aiohttp
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance, price):
    return (
        f"Виконай технічний аналіз для {symbol} на таймфреймі {timeframe.upper()}.
"
        f"- RSI: {rsi:.2f}, SMA: {sma:.2f}, EMA: {ema:.2f}\n"
        f"- MACD: {macd:.2f}, Сигнальна: {macd_signal:.2f}\n"
        f"- Bollinger Bands: Верхня {bb_upper:.2f}, Нижня {bb_lower:.2f}\n"
        f"- Тренд: {trend}, Підтримка: {support:.2f}, Опір: {resistance:.2f}\n"
        f"- Поточна ціна: {price:.5f}\n"
        "На основі цих даних:
"
        "1. Оціни ситуацію на ринку.
"
        "2. Визнач оптимальну позицію: LONG або SHORT.
"
        "3. Вкажи точку входу, стоп-лосс, тейк-профіт.
"
        "4. Вкажи орієнтовну тривалість угоди в годинах.
"
        "Формат відповіді строго у JSON:
"
        "{\n"
        "  \"position\": \"LONG або SHORT\",\n"
        "  \"entry_price\": \"число\",\n"
        "  \"take_profit\": \"число\",\n"
        "  \"stop_loss\": \"число\",\n"
        "  \"leverage\": \"число\",\n"
        "  \"duration_hours\": \"число\",\n"
        "  \"comment\": \"короткий опис ситуації\"\n"
        "}"
    )

async def generate_signal_description(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance, price):
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "user",
                "content": build_prompt(
                    symbol, timeframe, rsi, sma, ema, macd, macd_signal,
                    bb_upper, bb_lower, trend, support, resistance, price
                )
            }
        ],
        "temperature": 0.4
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(GROQ_API_URL, headers=HEADERS, json=payload) as resp:
            data = await resp.json()
            content = data['choices'][0]['message']['content']

            try:
                parsed = json.loads(content)
                return parsed
            except json.JSONDecodeError:
                return {
                    "position": "WAIT",
                    "entry_price": price,
                    "take_profit": price,
                    "stop_loss": price,
                    "leverage": "1",
                    "duration_hours": "1",
                    "comment": content[:100] + "..."
                }