import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ініціалізація бота
app = Flask(__name__)
bot = Bot(token=TOKEN)

# Налаштування Telegram-бота (ЦЕ ВАЖЛИВО!)
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Функція для обробки команди /start
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

# API маршрут для вебхука
@app.route("/webhook", methods=["POST"])
async def webhook():
    if not request.is_json:
        return "Invalid request", 400

    update = Update.de_json(request.get_json(), bot)

    # Ініціалізація перед обробкою повідомлень
    await application.initialize()
    
    # Обробка оновлення
    await application.process_update(update)

    return "ok", 200

# Запуск Flask-сервера
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Визначення порту
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.initialize())  # Ініціалізуємо бот
    app.run(host="0.0.0.0", port=port)
