import os
import logging
import asyncio
import threading
from flask import Flask, request
from telegram import Update, Bot, constants
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import openai
import datetime

# ==== CONFIG ====
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "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"
PORT = int(os.environ.get("PORT", 10000))

# ==== LOGGING ====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==== FLASK FOR RENDER ====
app = Flask(__name__)

@app.route('/')
def index():
    return 'Dexmate AI Bot is Live!'

# ==== OPENROUTER API ====
async def call_ai(prompt):
    import httpx
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://t.me/Dex_Ai_coderbot",
        "X-Title": "Dexmate AI Bot"
    }
    data = {
        "model": "openrouter/cinematika-7b",
        "messages": [{"role": "user", "content": prompt}]
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"]

# ==== TELEGRAM BOT ====
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(BOT_TOKEN)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.lower()
    user_id = update.message.from_user.id
    logger.info(f"Message from {user_id}: {user_msg}")

    if "hello" in user_msg:
        await update.message.reply_text("How are you? Do you need any help? How can I help you?")
    else:
        try:
            reply = await call_ai(update.message.text)
            await update.message.reply_text(reply[:4096])
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("❌ Sorry, I couldn’t process your request right now.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Nice photo! Want me to describe, caption or edit it?")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 Got your file! Need help with its contents?")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙️ Voice message received! (Voice to text coming soon...)")

bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
bot_app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
bot_app.add_handler(MessageHandler(filters.VOICE, handle_voice))

# ==== START BOT ====
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # Add handlers here
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

@app.before_request
def start_bot():
    if not hasattr(app, 'bot_started'):
        app.bot_started = True
        loop = asyncio.new_event_loop()
        threading.Thread(target=loop.run_until_complete, args=(main(),)).start()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT)


