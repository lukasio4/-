import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Отримуємо токен з змінних середовища
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ініціалізація бота
bot = Bot(token=TOKEN)
app = Flask(__name__)

# Обробник команди /start
async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

# Обробник звичайних повідомлень (ехо-бот)
async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

# Основний API маршрут для обробки вебхука
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    application.process_update(update)
    return "ok"

# Налаштування бота
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Запуск сервера Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443)
