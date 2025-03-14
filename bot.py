import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler

# Налаштовуємо логування для відстеження помилок
logging.basicConfig(level=logging.INFO)

# Отримуємо токен із середовища
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ініціалізуємо Flask додаток та Telegram Bot
app = Flask(__name__)
bot = Bot(token=TOKEN)

# Функція, яка обробляє команду /start
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

# Ініціалізуємо додаток Telegram Bot API
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Ініціалізація Telegram-бота
async def init_application():
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

# Стартуємо асинхронний запуск ініціалізації
asyncio.run(init_application())

@app.route("/webhook", methods=["POST"])
async def webhook():
    """Функція Webhook, яка приймає запити від Telegram"""
    try:
        data = request.get_json()
        update = Update.de_json(data, bot)
        await application.process_update(update)
        return "ok", 200
    except Exception as e:
        logging.error(f"Помилка у webhook: {e}")
        return "error", 500

# Запуск Flask-сервера
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)
