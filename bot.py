import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# Отримуємо токен
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ініціалізація Flask
app = Flask(__name__)

# Ініціалізація бота
bot = Bot(token=TOKEN)

# **Створюємо Application перед викликом initialize**
application = ApplicationBuilder().token(TOKEN).build()
application.initialize()  # Викликаємо після створення application
application.add_handler(CommandHandler("start", start))

# Обробка команди /start
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

# **API маршрут для вебхука**
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(), bot)
    await application.process_update(update)
    return "ok", 200

# Запуск сервера Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443)
