import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# Отримуємо токен
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ініціалізація бота
app = Flask(__name__)
bot = Bot(token=TOKEN)

# **Функція для обробки команди /start**
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

# **Коректна ініціалізація application**
application = ApplicationBuilder().token(TOKEN).build()
application.initialize()  # Виправляємо помилку з логів
application.add_handler(CommandHandler("start", start))  # Тепер 'start' точно існує

# API маршрут для вебхука (асинхронний)
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    asyncio.create_task(application.process_update(update))  # Асинхронний виклик
    return "ok", 200

# Запуск Flask-сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443)
