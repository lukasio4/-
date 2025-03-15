import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn
import requests

# Завантажуємо змінні середовища
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
WEBHOOK_URL = "https://fenix-bot-3w3i.onrender.com/webhook"

# Ініціалізація бота та сервера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Логування
logging.basicConfig(level=logging.INFO)

# Глобальна змінна для збереження вибору голосу
user_voice_preference = {}

# Функція генерації голосу
def generate_voice(text, user_id):
    try:
        voice_id = user_voice_preference.get(user_id, "nCqaTnIbLdME87OuQaZY")  # Віра за замовчуванням
        url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": text
        }
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            audio_path = "response.mp3"
            with open(audio_path, "wb") as f:
                f.write(response.content)
            logging.info(f"[LOG] Голосове повідомлення збережено: {audio_path}")
            return audio_path
        else:
            logging.error(f"[ERROR] Помилка генерації голосу: {response.text}")
            return None
    except Exception as e:
        logging.error(f"[ERROR] Помилка генерації голосу: {e}")
        return None

@app.post("/webhook")
async def webhook(update: dict):
    try:
        telegram_update = types.Update(**update)
        await dp.feed_update(bot, telegram_update)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"[ERROR] Webhook помилка: {e}")
        return {"status": "error"}

@dp.message(Command("start"))
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Жіночий", callback_data="voice_female"),
         InlineKeyboardButton(text="Чоловічий", callback_data="voice_male")]
    ])
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення, і я відповім голосом!\n\nВибери тип голосу:", reply_markup=keyboard)

@dp.callback_query()
async def set_voice_preference(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if callback_query.data == "voice_female":
        user_voice_preference[user_id] = "nCqaTnIbLdME87OuQaZY"  # Віра
        await callback_query.message.answer("✅ Голос змінено на Жіночий! Надішли мені голосове повідомлення.")
    elif callback_query.data == "voice_male":
        user_voice_preference[user_id] = "9Sj8ugvpK1DmcAXyvi3a"  # Олексій Некрасов
        await callback_query.message.answer("✅ Голос змінено на Чоловічий! Надішли мені голосове повідомлення.")
    await callback_query.answer()

@dp.message()
async def handle_voice(message: Message):
    user_id = message.from_user.id
    if message.voice:
        file_info = await bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)
        local_audio = "input.ogg"
        with open(local_audio, "wb") as f:
            f.write(downloaded_file.read())

        audio_response = generate_voice("Привіт! Це тестова відповідь.", user_id)

        if audio_response:
            from aiogram.types import FSInputFile

voice = FSInputFile(audio_response)  # Передаємо файл як FSInputFile
await message.answer_voice(voice)

        else:
            await message.answer("❌ Помилка генерації голосу!")

async def main():
    await bot.set_webhook(WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
