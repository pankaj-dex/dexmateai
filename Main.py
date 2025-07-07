from flask import Flask, request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import requests, json, os
from datetime import datetime
import asyncio
import threading

# ================== CONFIG ==================
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "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"
WEBHOOK_URL = f"https://dexmateai.onrender.com/{BOT_TOKEN}"  # Replace if needed

# =============== FLASK APP ==================
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Dexmate AI is Live!"

@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    if request.method == "POST":
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return "OK"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# =============== AI FUNCTION ===============
def ask_openrouter(prompt, model="mistralai/mixtral-8x7b-instruct"):
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful coding teacher."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ========== HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Python"), KeyboardButton("Java")],
        [KeyboardButton("C++"), KeyboardButton("JavaScript")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Choose a language to learn 👇", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 Thinking...")
    response = ask_openrouter(update.message.text)
    await update.message.reply_text(response)

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your Telegram ID: {update.message.from_user.id}")

# =========== MAIN ============
if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getid", getid))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start Flask server in new thread
    threading.Thread(target=run_flask).start()

    # Set webhook and run application
    async def run():
        await application.bot.set_webhook(WEBHOOK_URL)
        print("✅ Webhook set. Dexmate AI is Live.")
    asyncio.run(run())