import os
import logging
import httpx
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === CONFIG ===
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "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"
MODEL = "openai/gpt-3.5-turbo"

# === LOGGING ===
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
            data = res.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"AI error: {e}")
        return "❌ Sorry, something went wrong while generating a response."

# === HANDLERS ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await get_ai_response(update.message.text)
    await update.message.reply_text(reply)

async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 File received! I'll support file processing soon.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Voice received! Voice-to-text coming soon.")

# === START BOT ===
def main():
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app_telegram.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_files))
    app_telegram.add_handler(MessageHandler(filters.VOICE, handle_voice))

    logging.info("✅ Telegram bot is running...")
    app_telegram.run_polling()

if __name__ == '__main__':
    main()