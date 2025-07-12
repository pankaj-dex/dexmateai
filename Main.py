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
            return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return "⚠️ AI error. Please try again."

# === HANDLERS ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    reply = await get_ai_response(user_input)
    await update.message.reply_text(reply)

async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📁 File received! (Feature coming soon)")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Voice message received! (Voice-to-text coming soon)")

# === BOT STARTUP ===
async def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_files))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.wait_until_closed()
    await application.stop()
    await application.shutdown()

def start_bot():
    asyncio.run(run_bot())

# === FLASK APP ===
@app.route("/", methods=["GET", "HEAD"])
def index():
    return "✅ Dexmate AI is live!"

# === MAIN ===
if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=10000)