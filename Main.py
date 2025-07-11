import logging, os, aiofiles, asyncio, threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler, filters
)
import httpx

# ======== CONFIGURATION =========
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "your_openrouter_api_key_here"
MODEL = "openai/gpt-3.5-turbo"
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ======== AI RESPONSE FUNCTION =========
async def get_ai_response(message: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": message}]
                }
            )
            data = res.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return "⚠️ Sorry, I couldn't fetch a response."

# ======== HANDLERS =========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await get_ai_response(update.message.text)
    await update.message.reply_text(reply)

async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 File received! I'll support file processing soon.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Voice received! Voice-to-text coming soon.")

# ======== TELEGRAM BOT =========
def start_bot():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app_telegram.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_files))
    app_telegram.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app_telegram.run_polling()

# ======== FLASK + THREAD =========
@app.route("/", methods=["GET", "HEAD"])
def index():
    threading.Thread(target=start_bot).start()
    return "✅ Dexmate AI bot is running!"

# ======== MAIN =========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)