import os
import json
import aiohttp

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GROQ_API_KEY}",
}

def build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance, price):
    return (
        f"Монета: {symbol}\n"
        f"Таймфрейм: {timeframe}\n"
        f"Ціна: {price:.5f}$\n"
        f"RSI: {rsi:.5f}, SMA: {sma:.5f}, EMA: {ema:.5f}\n"
        f"MACD: {macd:.5f}, Сигнальна лінія MACD: {macd_signal:.5f}\n"
        f"Bollinger Bands: Верхня {bb_upper:.5f}$ / Нижня {bb_lower:.5f}$\n"
        f"Тренд: {trend}, Підтримка: {support:.5f}, Опір: {resistance:.5f}\n\n"
        "Зроби короткий технічний аналіз ситуації на ринку на основі вищенаведених індикаторів. "
        "Визнач потенційну торгову позицію (LONG або SHORT), точку входу, стоп-лосс, тейк-профіт, рекомендоване плече та орієнтовну тривалість угоди в годинах.\n"
        "Формат відповіді:\n"
        "{\n"
        "  \"position\": \"LONG або SHORT\",\n"
        "  \"entry_price\": \"...\",\n"
        "  \"take_profit\": \"...\",\n"
        "  \"stop_loss\": \"...\",\n"
        "  \"leverage\": \"...\",\n"
        "  \"duration_hours\": \"...\",\n"
        "  \"comment\": \"Короткий опис ситуації\"\n"
        "}\n"
        "Відповідай лише у форматі JSON українською."
    )

async def generate_signal_description(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance, price):
    prompt = build_prompt(symbol, timeframe, rsi, sma, ema, macd, macd_signal, bb_upper, bb_lower, trend, support, resistance, price)

    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(GROQ_API_URL, headers=HEADERS, json=data) as response:
            if response.status != 200:
                text = await response.text()
                return f"⚠️ Помилка від Groq: {response.status} {text}"

            result = await response.json()
            content = result["choices"][0]["message"]["content"]

            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                return f"⚠️ Невдалось розібрати JSON: {content}"

            try:
                entry = float(parsed.get("entry_price", price))
            except:
                entry = price

            try:
                take_profit = float(parsed.get("take_profit", price))
            except:
                take_profit = price

            try:
                stop_loss = float(parsed.get("stop_loss", ""))
            except:
                stop_loss = ""

            duration = parsed.get("duration_hours", "")
            position = parsed.get("position", "")
            comment = parsed.get("comment", "")

            return (
                f"- Позиція: {position}\n"
                f"- Точка входу: {entry:.5f}\n"
                f"- Тейк-профіт: {take_profit:.5f}\n"
                f"- Стоп-лосс: {stop_loss:.5f}\n"
                f"- Орієнтовний час: {duration} годин\n"
                f"- Опис ринкової ситуації: {comment}"
            )