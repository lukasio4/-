import os
import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn
from openai import OpenAI

# Завантаження змінних середовища
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://fenix-bot-3w3i.onrender.com/webhook"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Список голосів
VOICES = {
    "Жіночий": "nCqaTnIbLdME87OuQaZY",  # Віра
    "Чоловічий": "9Sj8ugvpK1DmcAXyvi3a"  # Олексій Некрасов
}

# Параметри за замовчуванням
user_voice_preferences = {}

# Функція генерації голосу

def generate_voice(user_id, text):
    try:
        voice_id = user_voice_preferences.get(user_id, "nCqaTnIbLdME87OuQaZY")  # За замовчуванням жіночий
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {"text": text}
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            audio_path = "response.mp3"
            with open(audio_path, "wb") as f:
                f.write(response.content)
            return audio_path
        else:
            logging.error(f"Помилка генерації голосу: {response.json()}")
            return None
    except Exception as e:
        logging.error(f"[ERROR] {e}")
        return None

# Функція обробки GPT-відповіді

def get_gpt_response(prompt):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        logging.error(f"GPT помилка: {e}")
        return "Вибач, я не можу зараз відповісти."

# Обробка webhook
@app.post("/webhook")
async def webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

# Обробка команди /start
@dp.message(Command("start"))
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Жіночий", callback_data="voice_female"),
         InlineKeyboardButton(text="Чоловічий", callback_data="voice_male")]
    ])
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення, і я відповім голосом!\n\nВибери тип голосу:",
                         reply_markup=keyboard)

# Обробка вибору голосу
@dp.callback_query()
async def change_voice(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if callback.data == "voice_female":
        user_voice_preferences[user_id] = "nCqaTnIbLdME87OuQaZY"
        await callback.message.answer("✅ Голос змінено на Жіночий! Надішли мені голосове повідомлення.")
    elif callback.data == "voice_male":
        user_voice_preferences[user_id] = "9Sj8ugvpK1DmcAXyvi3a"
        await callback.message.answer("✅ Голос змінено на Чоловічий! Надішли мені голосове повідомлення.")
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

        gpt_response = get_gpt_response("Користувач надіслав голосове повідомлення. Дай веселу відповідь.")
        audio_response = generate_voice(message.from_user.id, gpt_response)

        if audio_response:
            voice = FSInputFile(audio_response)
            await message.answer_voice(voice)
        else:
            await message.answer("❌ Помилка генерації голосу!")

async def main():
    await bot.set_webhook(WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
