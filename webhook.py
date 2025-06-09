async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Визначаємо chat_id
        if update.callback_query:
            await update.callback_query.answer()
            chat_id = update.callback_query.message.chat.id
        elif update.message:
            chat_id = update.message.chat.id
        else:
            return  # Якщо немає ні callback, ні message — вихід

        await context.bot.send_message(chat_id, "⏳ Очікую дані...")

        prices = get_crypto_prices()
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