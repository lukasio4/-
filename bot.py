import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ініціалізація Flask
app = Flask(__name__)
bot = Bot(token=TOKEN)

# Функція для обробки команди /start
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

# API маршрут для вебхука
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    application.process_update(update)
    return "ok"

# Налаштування Telegram-бота
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Запуск Flask-сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443)
