import requests
import os

# Отримуємо токен бота з середовищних змінних
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN не знайдено! Переконайся, що змінна середовища задана.")
else:
    # Запит на видалення вебхука
    response = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook")
    
    # Виводимо результат
    print(f"✅ Статус відповіді Telegram API: {response.status_code}")
    print(f"📩 Відповідь: {response.text}")