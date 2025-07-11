import os
import logging
import asyncio
import threading
from flask import Flask
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
import httpx
import json

# === YOUR API KEYS ===
BOT_TOKEN = "7866890680:AAfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "sk-or-v1-bd9437c745a4ece919192972ca1ba5795b336df4d836bd47e6c24b0dc991"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === FLASK SETUP ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Dexmate AI is Live on Render!"

# === AI RESPONSE FUNCTION ===
async def get_ai_response(message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"AI response error: {e}")
        return "❌ Error getting AI response. Please try again later."

# === HANDLERS ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    await update.message.reply_text("⏳ Thinking...")
    reply = await get_ai_response(message)
    await update.message.reply_text(reply)

async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📎 I received your file! I'll handle file support soon.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Voice received! Voice-to-text is coming soon.")

# === TELEGRAM BOT FUNCTION ===
async def run_bot():
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    bot_app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_files))
    bot_app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    await bot_app.run_polling()

# === THREAD FOR FLASK (RUN IN BACKGROUND) ===
def run_flask():
    app.run(host="0.0.0.0", port=10000)

# === MAIN START ===
if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    asyncio.run(run_bot())