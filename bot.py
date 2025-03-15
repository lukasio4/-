import os
import logging
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn
from openai import OpenAI
from elevenlabs import ElevenLabs

# Завантажуємо змінні середовища (API-ключі)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = f"https://fenix-bot-3w3i.onrender.com/webhook"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Доступні голоси
VOICES = {"male": "Adam", "female": "Bella"}

# Функція для отримання відповіді від GPT
async def get_gpt_response(text):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"[ERROR] GPT Помилка: {e}")
        return "Я не зміг придумати відповідь 😔"

# Генерація голосу
async def generate_voice(text, gender="female"):
    try:
        voice = VOICES.get(gender, "Bella")
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = elevenlabs_client.text_to_speech.convert(text=text, voice=voice)

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
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Жіночий", callback_data="voice_female"),
         InlineKeyboardButton(text="Чоловічий", callback_data="voice_male")]
    ])
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення, і я відповім голосом!\n\nВибери тип голосу:", reply_markup=keyboard)

@dp.callback_query()
async def set_voice_preference(callback: types.CallbackQuery):
    user_choice = callback.data.split("_")[1]
    await callback.answer(f"Ви обрали {user_choice} голос!")
    await callback.message.answer("Тепер відправте голосове повідомлення!")

@dp.message()
async def handle_voice(message: Message):
    if message.voice:
        file_info = await bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)
        local_audio = "input.ogg"
        with open(local_audio, "wb") as f:
            f.write(downloaded_file.read())

        # Отримуємо відповідь від GPT
        gpt_response = await get_gpt_response("Що сказати у відповідь?")

        # Генеруємо голосову відповідь
        audio_response = await generate_voice(gpt_response, gender="female")

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
