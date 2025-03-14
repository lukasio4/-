# 🚀 FeniX_Bot - Telegram AI Bot with Webhook

## 🔧 Installation

### 1️⃣ Clone the repository
```sh
git clone https://github.com/YOUR_USERNAME/FeniX_Bot.git
cd FeniX_Bot
```

### 2️⃣ Install dependencies
```sh
pip install -r requirements.txt
```

### 3️⃣ Set environment variables
Create a `.env` file and add:
```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

## 🚀 Deployment on Render
1. Create a new **Web Service** on [Render](https://dashboard.render.com/).
2. Upload this repository.
3. Set **Start Command** to:
   ```sh
   uvicorn bot:app --host 0.0.0.0 --port 8000
   ```
4. Add environment variables (API keys).
5. Click **Deploy**.

## 📞 Support
If you have issues, contact [Telegram](https://t.me/your_username).
