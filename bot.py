import os
import asyncio
import threading
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, ApplicationBuilder, CommandHandler

# Отримуємо токен
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ініціалізація Flask
app = Flask(__name__)
bot = Bot(token=TOKEN)

# Функція для обробки команди /start
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

# Створюємо додаток Telegram
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Ініціалізація додатку Telegram
async def init_application():
    await application.initialize()
    await application.start()

# Запускаємо Telegram бот у фоні
threading.Thread(target=lambda: asyncio.run(init_application()), daemon=True).start()

# Flask-ендпоінт для вебхука
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(), bot)
    await application.process_update(update)
    return "ok", 200

# Запуск сервера Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)
