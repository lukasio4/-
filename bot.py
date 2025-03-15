import os
import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn
import openai

# Завантажуємо змінні середовища (API-ключі)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = f"https://fenix-bot-3w3i.onrender.com/webhook"
GPT_MODEL = "gpt-4"
GPT_ENDPOINT = "https://chatgpt.com/g/g-6786c163b4b4819193ffe013b5d6b26d-fenix-2-1"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Перевіряємо, чи API-ключі доступні
print("[DEBUG] ELEVENLABS_API_KEY =", ELEVENLABS_API_KEY)
print("[DEBUG] OPENAI_API_KEY =", OPENAI_API_KEY)

def generate_voice(text, voice="Bella"):
    try:
        voices = {"female": "tC4vX6Z71D2o0o0HWGWe", "male": "EXAVITQu4vr4xnSDxMaL"}
        voice_id = voices[voice]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }

        data = {"text": text}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 401:
            print(f"[ERROR] Невірний API-ключ! Перевір API-ключ у ElevenLabs.")
            return None

        if response.status_code != 200:
            print(f"[ERROR] Помилка генерації голосу: {response.status_code}, {response.text}")
            return None

        audio_path = "response.mp3"
        with open(audio_path, "wb") as f:
            f.write(response.content)

        print(f"[LOG] Голосове повідомлення збережено: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"[ERROR] Помилка генерації голосу: {e}")
        return None

def generate_gpt_response(prompt):
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        data = {"model": GPT_MODEL, "messages": [{"role": "user", "content": prompt}]}
        response = requests.post(GPT_ENDPOINT, json=data, headers=headers)
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] GPT відповідь не отримано: {e}")
        return "Вибач, не можу зараз відповісти."

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
    await message.answer("🔥 Привіт! Надішли мені голосове повідомлення або текст, і я відповім!")

@dp.message()
async def handle_message(message: Message):
    if message.voice:
        file_info = await bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)
        local_audio = "input.ogg"
        with open(local_audio, "wb") as f:
            f.write(downloaded_file.read())

        # Використовуємо GPT для створення розумної відповіді
        gpt_response = generate_gpt_response("Що ти скажеш на це?")
        voice_gender = "female" if "вона" in gpt_response else "male"

        # Генеруємо голосову відповідь
        audio_response = generate_voice(gpt_response, voice=voice_gender)

        if audio_response:
            audio_file = FSInputFile(audio_response)  # Коректний формат файлу
            await message.answer_voice(audio_file)
        else:
            await message.answer("❌ Помилка генерації голосу!")
    else:
        text_response = generate_gpt_response(message.text)
        await message.answer(text_response)

async def main():
    await bot.set_webhook(WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
if __name__ == "__main__":
    asyncio.run(main())

