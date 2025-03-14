import os
import asyncio
import threading
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = Flask(__name__)
bot = Bot(token=TOKEN)

async def start(update: Update, context):
    await update.message.reply_text("Привіт! Я твій бот!")

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    threading.Thread(target=lambda: asyncio.run(application.process_update(update))).start()
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))  
    app.run(host="0.0.0.0", port=port)
