import os
import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn
from elevenlabs import ElevenLabs

# Завантажуємо змінні середовища
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://fenix-bot-3w3i.onrender.com/webhook"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Логування
logging.basicConfig(level=logging.INFO)

def get_gpt_response(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        logging.error(f"GPT помилка: {response.status_code}, {response.text}")
        return "Вибач, я не зміг сформувати відповідь."

def generate_voice(text, voice="Bella"):
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = elevenlabs_client.text_to_speech.convert(text=text, voice=voice)
        audio_path = "response.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio)
        logging.info(f"[LOG] Голосове повідомлення збережено: {audio_path}")
        return audio_path
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

        # Отримуємо відповідь GPT
        gpt_response = get_gpt_response("Що відповісти на це голосове повідомлення?")
        logging.info(f"[GPT] Відповідь: {gpt_response}")

        # Вибір голосу (жіночий або чоловічий)
        voice = "Bella" if "жіночий" in gpt_response else "Adam"
        audio_response = generate_voice(gpt_response, voice)

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
