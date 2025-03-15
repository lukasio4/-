import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn
from gtts import gTTS

# Завантажуємо змінні середовища
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = "https://fenix-bot-3w3i.onrender.com/webhook"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Функція для генерації голосового повідомлення
def generate_voice(text, lang="uk"):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_path = "response.mp3"
        tts.save(audio_path)
        print(f"[LOG] Голосове повідомлення збережено: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"[ERROR] Помилка генерації голосу: {e}")
        return None

# Webhook
@app.post("/webhook")
async def webhook(update: dict):
    try:
        telegram_update = types.Update(**update)
        await dp.feed_update(bot, telegram_update)
        print("[LOG] Webhook отримав оновлення:", update)
        return {"status": "ok"}
    except Exception as e:
        print(f"[ERROR] Webhook помилка: {e}")
        return {"status": "error"}

# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Жіночий голос 🔊")]],
        resize_keyboard=True,
    )
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення, і я відповім голосом!", reply_markup=keyboard)

# Обробка голосових повідомлень
@dp.message()
async def handle_voice(message: Message):
    if message.voice:
        file_info = await bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)
        local_audio = "input.ogg"

        with open(local_audio, "wb") as f:
            f.write(downloaded_file.read())

        # Генеруємо голосову відповідь
        audio_response = generate_voice("Привіт! Це тестова відповідь.")

        if audio_response:
            with open(audio_response, "rb") as audio:
                await message.answer_voice(types.InputFile(audio_response))
        else:
            await message.answer("❌ Помилка генерації голосу!")

# Головна функція
async def main():
    await bot.set_webhook(WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
