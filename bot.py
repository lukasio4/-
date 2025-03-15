import os
import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
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

# Налаштування логування
logging.basicConfig(level=logging.INFO)
user_voice_preference = {}

# Голоси
VOICES = {
    "female": "nCqaTnIbLdME87OuQaZY",  # Віра
    "male": "9Sj8ugvpK1DmcAXyvi3a"   # Олексій Некрасов
}

# Функція генерації голосу
def generate_voice(text, voice_id):
    try:
        url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id
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
            logging.error("Помилка генерації голосу: " + response.text)
            return None
    except Exception as e:
        logging.error(f"Помилка генерації голосу: {e}")
        return None

# Функція обробки повідомлення через GPT
async def get_gpt_response(prompt):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        logging.error(f"Помилка GPT: {e}")
        return "Вибач, сталася помилка під час обробки відповіді."

# Вебхук
@app.post("/webhook")
async def webhook(update: dict):
    try:
        telegram_update = types.Update(**update)
        await dp.feed_update(bot, telegram_update)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Помилка вебхука: {e}")
        return {"status": "error"}

# Обробник команди старт
@dp.message(Command("start"))
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Жіночий", callback_data="voice_female"),
         InlineKeyboardButton(text="Чоловічий", callback_data="voice_male")]
    ])
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення, і я відповім голосом!\n\nВибери тип голосу:", reply_markup=keyboard)

# Обробник вибору голосу
@dp.callback_query()
async def select_voice(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if callback_query.data == "voice_female":
        user_voice_preference[user_id] = "female"
        await callback_query.message.answer("✅ Голос змінено на Жіночий! Надішли мені голосове повідомлення.")
    elif callback_query.data == "voice_male":
        user_voice_preference[user_id] = "male"
        await callback_query.message.answer("✅ Голос змінено на Чоловічий! Надішли мені голосове повідомлення.")
    await callback_query.answer()

# Обробка голосових повідомлень
@dp.message()
async def handle_voice(message: Message):
    if message.voice:
        user_id = message.from_user.id
        voice_type = user_voice_preference.get(user_id, "female")
        file_info = await bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)
        local_audio = "input.ogg"
        with open(local_audio, "wb") as f:
            f.write(downloaded_file.read())
        gpt_response = await get_gpt_response("Опиши веселу відповідь на голосове повідомлення.")
        audio_response = generate_voice(gpt_response, VOICES[voice_type])
        if audio_response:
            with open(audio_response, "rb") as audio:
                await message.answer_voice(audio)
        else:
            await message.answer("❌ Помилка генерації голосу!")

# Запуск бота
async def main():
    await bot.set_webhook(WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
