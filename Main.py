import os
import logging
import asyncio
import aiofiles
from datetime import datetime
from flask import Flask
from telegram import Update, File, Bot
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    MessageHandler, filters
)
import httpx
import threading

# === FILLED CONFIG ===
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "sk-or-v1-bd9437c745a4ece919192972ca1ba5795b336df4d836bd47e6c24b0dc991"  # Your key
OPENROUTER_MODEL = "openchat/openchat-7b:free"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === FLASK FOR RENDER ===
app = Flask(__name__)

# === LOG CHAT FUNCTION ===
async def log_chat(user_id, username, message):
    os.makedirs("logs", exist_ok=True)
    async with aiofiles.open(f"logs/{user_id}.txt", mode="a") as f:
        await f.write(f"{datetime.now()} | {username} | {message}\n")

# === GENERATE AI MESSAGE ===
async def generate_ai_reply(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://dexmateai.onrender.com",
            "X-Title": "Dexmate AI"
        }
        data = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers, json=data, timeout=60
            )
            result = response.json()
            return result['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ AI Error: {e}"

# === TEXT MESSAGE HANDLER ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message.text
    await log_chat(user.id, user.username or "Unknown", msg)
    await update.message.reply_text("🤖 Thinking...")
    reply = await generate_ai_reply(msg)
    await update.message.reply_text(reply)

# === FILE HANDLER (Photo/Doc) ===
async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    file: File = None
    if update.message.document:
        file = await update.message.document.get_file()
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
    if file:
        path = f"uploads/{user.id}_{datetime.now().timestamp()}.bin"
        os.makedirs("uploads", exist_ok=True)
        await file.download_to_drive(path)
        await update.message.reply_text("✅ File received and saved!")

# === VOICE HANDLER ===
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    voice = update.message.voice
    file = await voice.get_file()
    path = f"uploads/{user.id}_{datetime.now().timestamp()}.ogg"
    os.makedirs("uploads", exist_ok=True)
    await file.download_to_drive(path)
    await update.message.reply_text("🎤 Voice saved! Voice-to-text coming soon.")

# === MAIN BOT FUNCTION ===
async def bot_main():
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    bot_app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_files))
    bot_app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    await bot_app.run_polling()

# === HOMEPAGE ===
@app.route('/')
def home():
    return "✅ Dexmate AI is Live on Render!"

# === START BOT THREAD ===
@app.before_request
def run_bot():
    if not hasattr(app, 'bot_started'):
        app.bot_started = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        thread = threading.Thread(target=loop.run_until_complete, args=(bot_main(),))
        thread.start()



# === FLASK SERVER ===
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)