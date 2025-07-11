import os
import logging
import asyncio
import threading
from flask import Flask
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import httpx

# === YOUR API KEYS ===
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "sk-or-v1-bd9437c745a4ece919192972ca1ba5795b336df4d836bd47e6c24b0dc991"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === FLASK SERVER FOR RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Dexmate AI Bot is running."

# === AI REPLY FUNCTION ===
async def get_ai_response(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://dexmateai.onrender.com",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openrouter/cinematika-7b",
        "messages": [
            {"role": "system", "content": "You're an expert helpful AI assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return "❌ Sorry, I couldn't fetch a response."

# === TELEGRAM HANDLERS ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text in ["hi", "hello", "hey"]:
        await update.message.reply_text("👋 Hello! How are you? Do you need any help?")
    else:
        reply = await get_ai_response(update.message.text)
        await update.message.reply_text(reply)

async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 File received! I'll support file processing soon.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Voice received! Voice-to-text coming soon.")

# === RUN TELEGRAM BOT ===
async def run_bot():
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app_telegram.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_files))
    app_telegram.add_handler(MessageHandler(filters.VOICE, handle_voice))
    logger.info("Starting Telegram bot...")
    await app_telegram.initialize()
    await app_telegram.start()
    await app_telegram.updater.start_polling()
    # We won't use app_telegram.updater.idle() because it's deprecated

# === START FUNCTION (THREAD) ===
def start():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

# === MAIN START ===
if __name__ == '__main__':
    threading.Thread(target=start).start()
    app.run(host='0.0.0.0', port=10000)
