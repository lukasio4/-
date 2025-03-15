import os
import requests
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn

# Завантажуємо змінні середовища (API-ключі)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
WEBHOOK_URL = f"https://fenix-bot-3w3i.onrender.com/webhook"

# Voice IDs для вибору голосу
VOICE_IDS = {
    "Жіночий": "nCqaTnIbLdME87OuQaZY",  # Віра
    "Чоловічий": "9Sj8ugvpK1DmcAXyvi3a"  # Олексій Некрасов
}

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Логування
logging.basicConfig(level=logging.INFO)

# Словник для збереження вибору голосу
user_voice_choice = {}


# Функція генерації голосу
def generate_voice(text, voice_type="Жіночий"):
    try:
        voice_id = VOICE_IDS.get(voice_type, VOICE_IDS["Жіночий"])  # За замовчуванням жіночий голос
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }

        data = {
            "text": text,
            "model_id": "eleven_multilingual_v1"
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            audio_path = "response.mp3"
            with open(audio_path, "wb") as f:
                f.write(response.content)
            return audio_path
        else:
            logging.error(f"[ERROR] Помилка генерації голосу: {response.text}")
            return None
    except Exception as e:
        logging.error(f"[ERROR] Виникла помилка: {e}")
        return None


@app.post("/webhook")
async def webhook(update: dict):
    try:
        telegram_update = types.Update(**update)
        await dp.feed_update(bot, telegram_update)
        logging.info(f"[LOG] Webhook отримав оновлення: {update}")
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"[ERROR] Webhook помилка: {e}")
        return {"status": "error"}


@dp.message(Command("start"))
async def start_command(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Жіночий"), KeyboardButton(text="Чоловічий")]
        ],
        resize_keyboard=True
    )
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення, і я відповім голосом!\n\nВибери тип голосу:", reply_markup=keyboard)


@dp.message()
async def handle_voice(message: Message):
    if message.text in VOICE_IDS:
        user_voice_choice[message.from_user.id] = message.text
        await message.answer(f"✅ Голос змінено на {message.text}! Надішли мені голосове повідомлення.")
        return

    if message.voice:
        file_info = await bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)
        local_audio = "input.ogg"
        with open(local_audio, "wb") as f:
            f.write(downloaded_file.read())

        # Отримуємо вибір голосу користувача або ставимо жіночий за замовчуванням
        voice_type = user_voice_choice.get(message.from_user.id, "Жіночий")

        # Генеруємо голосову відповідь
        audio_response = generate_voice("Привіт! Це тестова відповідь.", voice_type)

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
