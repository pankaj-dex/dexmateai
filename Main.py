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

# === YOUR API KEYS ===
BOT_TOKEN = "7866890680:AAfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "sk-or-v1-bd9437c745a4ece919192972ca1ba5795b336df4d836bd47e6c24b0dc991"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === FLASK APP ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Dexmate AI is Live on Render!"

# === AI CALL FUNCTION ===
async def get_ai_response(message):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": message}]
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, json=data, timeout=30)
            res.raise_for_status()
            reply = res.json()['choices'][0]['message']['content']
            return reply
    except Exception as e:
        logger.error(f"OpenRouter error: {e}")
        return "❌ Error generating response."

# === TELEGRAM HANDLERS ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("⏳ Thinking...")
    reply = await get_ai_response(text)
    await update.message.reply_text(reply)

async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📎 File received. I'll support file processing soon!")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Voice received. Voice-to-text coming soon!")

# === TELEGRAM BOT RUN FUNCTION ===
async def telegram_main():
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    bot_app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_files))
    bot_app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    await bot_app.run_polling()

# === START BOT IN BACKGROUND THREAD ===
def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telegram_main())

# === MAIN ===
if __name__ == '__main__':
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=10000)