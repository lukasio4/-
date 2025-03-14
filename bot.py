import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn
from elevenlabs import ElevenLabs

# Завантажуємо змінні середовища (API-ключі)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
WEBHOOK_URL = f"https://fenix-bot-3w3i.onrender.com/webhook"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

def generate_voice(text):
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = elevenlabs_client.text_to_speech.convert(text=text, voice="Bella")

        audio_path = "response.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio)

        print(f"[LOG] Голосове повідомлення збережено: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"[ERROR] Помилка генерації голосу: {e}")
        return None

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

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення, і я відповім голосом!")

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
                await message.answer_voice(audio)
        else:
            await message.answer("❌ Помилка генерації голосу!")

async def main():
    await bot.set_webhook(WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
