import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler

# Отримуємо токен із змінних середовища
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не знайдено у змінних середовища!")

# Ініціалізація Flask
app = Flask(__name__)

# Ініціалізація Telegram бота
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Функція для команди /start
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

# Додаємо команду в хендлери
application.add_handler(CommandHandler("start", start))

# Ініціалізація та запуск бота
async def run_bot():
    await application.initialize()
    await application.start()
    logging.info("Bot started!")

# Запускаємо асинхронний процес Telegram бота перед обробкою оновлень
@app.before_first_request
def activate_bot():
    asyncio.create_task(run_bot())

# Вебхук для обробки оновлень
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return "ok", 200

# Запуск Flask-сервера
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)
