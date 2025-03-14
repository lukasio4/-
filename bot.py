import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler

# Включаємо логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Отримуємо токен з середовища
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не задано в середовищі!")

# Ініціалізація Flask
app = Flask(__name__)

# Ініціалізація бота
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Обробник команди /start
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

# Додаємо команду /start
application.add_handler(CommandHandler("start", start))

# Ініціалізація додатку перед запуском
async def init_application():
    await application.initialize()
    await application.start()
    logger.info("Бот запущено!")

# Запускаємо ініціалізацію асинхронно
asyncio.run(init_application())

# Webhook маршрут
@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        update = Update.de_json(request.get_json(), bot)
        await application.process_update(update)
        return "ok", 200
    except Exception as e:
        logger.error(f"Помилка обробки webhook: {e}")
        return "error", 500

# Запускаємо Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)
