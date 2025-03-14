import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = f"https://fenix-bot-3w3i.onrender.com/webhook"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

@app.post("/webhook")
async def webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення, і я відповім голосом!")

async def main():
    await bot.set_webhook(WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
