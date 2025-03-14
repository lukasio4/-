import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# Отримуємо токен із змінних середовища
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ініціалізація Flask (з `async_mode=True` для коректної роботи асинхронних функцій)
app = Flask(__name__, async_mode=True)

# Ініціалізація Telegram-бота
application = ApplicationBuilder().token(TOKEN).build()
bot = Bot(token=TOKEN)

# Функція для обробки команди /start
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

application.add_handler(CommandHandler("start", start))

# API маршрут для обробки вебхука
@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.is_json:
        update = Update.de_json(request.get_json(), bot)
        await application.process_update(update)
        return "ok", 200
    return "Invalid request", 400

# Запуск сервера
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))  # Використовуємо порт із середовища або 8443 за замовчуванням
    app.run(host="0.0.0.0", port=port)
