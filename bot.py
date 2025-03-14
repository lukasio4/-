import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# Отримання токена бота з середовищних змінних
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ініціалізація Flask
app = Flask(__name__)

# Ініціалізація Telegram-бота
application = ApplicationBuilder().token(TOKEN).build()

# Функція для обробки команди /start
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

# Додавання команди start до обробника
application.add_handler(CommandHandler("start", start))

# API маршрут для вебхука
@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(), application.bot)
        await application.process_update(update)
        return "ok", 200

# Запуск сервера
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))  # Використовуємо стандартний порт 8443 або той, що передано
    app.run(host="0.0.0.0", port=port)
