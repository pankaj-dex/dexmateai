from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    MessageHandler, filters
)
from flask import Flask, request
import requests
import os
import json
import threading
from datetime import datetime

# ==========================
# 🔐 BOT & API KEYS
# ==========================
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "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"
DATA_FILE = "users_data.json"

# ==========================
# 🔔 FLASK SETUP
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Dexmate AI is live!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ==========================
# 🧠 AI RESPONSE HANDLER
# ==========================
def ask_openrouter(prompt):
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mixtral-8x7b-instruct",
                "messages": [
                    {"role": "system", "content": "You are a helpful coding teacher."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==========================
# 📊 USER TRACKING
# ==========================
def load_user_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_user_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def increment_user_count(user_id):
    data = load_user_data()
    uid = str(user_id)
    today_str = datetime.now().strftime("%Y-%m-%d")
    if uid not in data:
        data[uid] = {"count": 0, "date": today_str, "ad_index": 0}
    if data[uid]["date"] != today_str:
        data[uid]["count"] = 0
        data[uid]["date"] = today_str
    data[uid]["count"] += 1
    save_user_data(data)
    return data[uid]["count"]

# ==========================
# 🧠 MAIN HANDLERS
# ==========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    count = increment_user_count(user_id)

    if datetime.now() < datetime(2025, 8, 16) and count > 5:
        await update.message.reply_text("🚫 Free daily limit reached! Come back tomorrow.")
        return

    text = update.message.text
    await update.message.reply_text("🧠 Thinking...")
    response = ask_openrouter(text)
    await update.message.reply_text(response)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Python"), KeyboardButton("C++")],
        [KeyboardButton("Java"), KeyboardButton("JavaScript")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Welcome to Dexmate AI!\nChoose your language:", reply_markup=reply_markup)

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    await update.message.reply_text(f"🆔 Your Telegram ID: {uid}")

# ==========================
# 🚀 RUN BOT + FLASK
# ==========================
if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("getid", get_id))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start Flask in background
    threading.Thread(target=run_flask).start()

    # Set webhook for Render deployment
    application.bot.set_webhook(f"https://dexmateai.onrender.com/{BOT_TOKEN}")
    print("✅ Dexmate AI deployed with webhook")