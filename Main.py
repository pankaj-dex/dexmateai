import os
import json
import time
import uuid
import logging
import asyncio
import threading
import aiohttp
import httpx

from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==== Fill Your API Keys ====
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "sk-or-v1-bd9437c745a4ece919192972ca1ba5795b336df4d836bd47e6c24b0dc991"

# ==== Set up logging ====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==== Create Flask app ====
app = Flask(__name__)

# ==== Create Telegram bot application ====
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# ==== Basic Hello Command ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I am Dexmate AI. How can I assist you today?")

# ==== Handle Any Message ====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Friendly response to greetings
    if text.lower() in ["hi", "hello", "hey"]:
        await update.message.reply_text("How are you? Do you need any help? 😊")
        return

    # AI-powered code assistant
    await update.message.reply_text("⏳ Generating response with AI...")
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        body = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": text}],
        }
        async with httpx.AsyncClient() as client:
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
            data = res.json()
            response = data["choices"][0]["message"]["content"].strip()
            await update.message.reply_text(response)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("⚠️ Sorry, I couldn't generate a response.")

# ==== Add Handlers ====
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ==== Bot Running Function ====
async def run_bot():
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    await bot_app.updater.idle()

# ==== Flask Route ====
@app.route("/", methods=["GET"])
def home():
    return "🤖 Dexmate AI bot is live!"

# ==== Start Everything in Threads ====
def start():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

if __name__ == "__main__":
    threading.Thread(target=start).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
