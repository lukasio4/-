import os
import logging
import asyncio
import json
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn

# Завантажуємо змінні середовища
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://fenix-bot-3w3i.onrender.com/webhook"

# Ініціалізація бота та FastAPI
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Варіанти голосів
VOICES = {"female": "Віра", "male": "Олексій Некрасов"}
user_voice_preferences = {}

# Функція виклику OpenAI GPT-3.5
async def get_gpt_response(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": "Ти веселий AI, який жартує"},
                     {"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return "Не вдалося отримати відповідь GPT."

# Функція генерації голосу
async def generate_voice(text, user_id):
    voice = user_voice_preferences.get(user_id, "female")
    selected_voice = VOICES.get(voice, "Віра")
    
    url = "https://api.elevenlabs.io/v1/text-to-speech"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    payload = {"text": text, "voice": selected_voice}
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        audio_path = "response.mp3"
        with open(audio_path, "wb") as f:
            f.write(response.content)
        return audio_path
    else:
        return None

# Webhook приймає оновлення від Telegram
@app.post("/webhook")
async def webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

# Обробник команди старт
@dp.message(Command("start"))
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Жіночий", callback_data="voice_female"),
         InlineKeyboardButton(text="Чоловічий", callback_data="voice_male")]
    ])
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення, і я відповім голосом!\n\nВибери тип голосу:", reply_markup=keyboard)

# Обробка натискання кнопки вибору голосу
@dp.callback_query()
async def voice_selection(callback: types.CallbackQuery):
    if callback.data == "voice_female":
        user_voice_preferences[callback.from_user.id] = "female"
        await callback.message.answer("Ви вибрали жіночий голос.")
    elif callback.data == "voice_male":
        user_voice_preferences[callback.from_user.id] = "male"
        await callback.message.answer("Ви вибрали чоловічий голос.")
    await callback.answer()

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

        gpt_response = await get_gpt_response("Користувач надіслав голосове повідомлення. Відповідай йому весело.")
        audio_response = await generate_voice(gpt_response, message.from_user.id)

        if audio_response:
            with open(audio_response, "rb") as audio:
                await message.answer_voice(types.InputFile(audio))
        else:
            await message.answer("❌ Помилка генерації голосу!")

# Запуск
async def main():
    await bot.set_webhook(WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())


