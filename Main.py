import os, asyncio, logging, threading, httpx
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === CONFIG ===
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "your_openrouter_api_key_here"
MODEL = "openai/gpt-3.5-turbo"

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# === AI RESPONSE ===
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
            return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(f"AI response error: {e}")
        return "⚠️ Sorry, an error occurred while processing your message."

# === HANDLERS ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = await get_ai_response(user_message)
    await update.message.reply_text(reply)

async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 File received! File processing support coming soon.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Voice received! Voice-to-text support coming soon.")

# === START TELEGRAM BOT ===
def start_bot():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app_telegram.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_files))
    app_telegram.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app_telegram.run_polling()

# === START ===
if __name__ == '__main__':
    threading.Thread(target=start_bot).start()
