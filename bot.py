import os
import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn
from openai import OpenAI
from elevenlabs import generate, play, set_api_key

# Завантажуємо змінні середовища
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://fenix-bot-3w3i.onrender.com/webhook"

# Ініціалізація бота та FastAPI
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Ініціалізація ElevenLabs API
set_api_key(ELEVENLABS_API_KEY)

# Варіанти голосів
VOICES = {
    "Жіночий": "nCqaTnIbLdME87OuQaZY",  # Віра
    "Чоловічий": "9Sj8ugvpK1DmcAXyvi3a"  # Олексій Некрасов
}
user_voices = {}

# Функція генерації голосу
def generate_voice(text, voice_id):
    try:
        audio = generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v1"
        )
        audio_path = "response.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio)
        return audio_path
    except Exception as e:
        logging.error(f"Помилка генерації голосу: {e}")
        return None

# Функція генерації відповіді GPT
def get_gpt_response(prompt):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.Completion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Ти веселий помічник!"},
                      {"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Помилка GPT: {e}")
        return "Вибач, я не зміг зрозуміти запит."

@app.post("/webhook")
async def webhook(update: dict):
    try:
        telegram_update = types.Update(**update)
        await dp.feed_update(bot, telegram_update)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Webhook помилка: {e}")
        return {"status": "error"}

@dp.message(Command("start"))
async def start_command(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("Жіночий"), KeyboardButton("Чоловічий")]],
        resize_keyboard=True
    )
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення, і я відповім голосом!\n\nВибери тип голосу:",
                         reply_markup=keyboard)

@dp.message()
async def handle_voice(message: Message):
    if message.text in VOICES:
        user_voices[message.from_user.id] = VOICES[message.text]
        await message.answer(f"✅ Голос змінено на {message.text}! Надішли мені голосове повідомлення.")
        return
    
    if message.voice:
        file_info = await bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)
        local_audio = "input.ogg"
        with open(local_audio, "wb") as f:
            f.write(downloaded_file.read())
        
        text_response = get_gpt_response("Користувач сказав: [голосове повідомлення]")
        voice_id = user_voices.get(message.from_user.id, VOICES["Жіночий"])
        audio_response = generate_voice(text_response, voice_id)

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
