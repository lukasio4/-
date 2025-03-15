import requests
import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from fastapi import FastAPI
import uvicorn
from gtts import gTTS

# Логування
logging.basicConfig(level=logging.INFO)

# Отримуємо токен бота з середовища
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не знайдено! Переконайся, що змінна середовища задана.")

# Видаляємо вебхук перед стартом (бо Render не дає терміналу)
def delete_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    response = requests.post(url)
    logging.info(f"🔄 Видалення вебхука: {response.status_code} | {response.text}")

delete_webhook()  # Виконується один раз при старті

# Створюємо об'єкти бота та диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# Функція генерації голосу
async def text_to_speech(text: str, chat_id: int):
    try:
        tts = gTTS(text=text, lang='uk')
        filename = f"voice_{chat_id}.mp3"
        tts.save(filename)
        return filename
    except Exception as e:
        logging.error(f"Помилка генерації голосу: {e}")
        return None

# Обробник команди /start
@dp.message()
async def start_handler(message: Message):
    if message.text == "/start":
        await message.answer("🔥 Привіт! Надішли мені текст, і я його озвучу!")

# Обробник текстових повідомлень
@dp.message()
async def text_handler(message: Message):
    chat_id = message.chat.id
    text = message.text
    
    voice_file = await text_to_speech(text, chat_id)
    
    if voice_file:
        with open(voice_file, "rb") as audio:
            await bot.send_voice(chat_id, audio)
        os.remove(voice_file)
    else:
        await message.answer("❌ Помилка генерації голосу!")

# Запуск бота
async def start_bot():
    await dp.start_polling(bot)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(start_bot())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
