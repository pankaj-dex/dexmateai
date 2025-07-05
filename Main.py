# Dexmate AI - Free Mode (until 16 August 2025)

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import requests, json, os
from datetime import datetime
from flask import Flask
import threading

# ========== KEYS & CONSTANTS ==========
import os
BOT_TOKEN = os.environ.get("7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA") 

OPENROUTER_API_KEY = os.environ.get("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") 
DATA_FILE = "users_data.json"
ADS = [
    "💡 Dexmate Pro launches 16 August with advanced features!",
    "🚀 Love Dexmate? Share it with friends!",
    "📢 Follow us @dexmateai for coding tips!"
]

# ========== FLASK SERVER ==========
app_flask = Flask(__name__)

@app_flask.route('/')
def index():
    return "Dexmate AI is live (Free Mode)"

def run_flask():
    app_flask.run(host='0.0.0.0', port=8080)

# ========== USER DATA SYSTEM ==========

def load_user_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_user_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def is_premium_period():
    today = datetime.now()
    return today >= datetime(2025, 8, 16)

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
    return data[uid]["count"], data[uid]["ad_index"]

def update_ad_index(user_id, index):
    data = load_user_data()
    uid = str(user_id)
    if uid in data:
        data[uid]["ad_index"] = index
        save_user_data(data)

# ========== AI FUNCTION ==========

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

# ========== BOT HANDLERS ==========

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip().lower()
    count, ad_index = increment_user_count(user_id)

    if not is_premium_period() and count > 5:
        await update.message.reply_text("🚫 Free daily limit reached! Come back tomorrow.")
        return

    if text == "start":
        keyboard = [
            [KeyboardButton("Python"), KeyboardButton("Java")],
            [KeyboardButton("C++"), KeyboardButton("JavaScript")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("👇 What language do you want to learn?", reply_markup=reply_markup)
    else:
        await update.message.reply_text("🧠 Thinking...")
        answer = ask_openrouter(text)
        await update.message.reply_text(answer)

        if count % 3 == 0:
            await update.message.reply_text(ADS[ad_index % len(ADS)])
            update_ad_index(user_id, ad_index + 1)

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    await update.message.reply_text(f"🆔 Your Telegram ID: {uid}")

# ========== RUN APP ==========

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CommandHandler("getid", get_id))

    print("✅ Dexmate AI Bot is Live (Free Mode)")
   #app.run_polling()
    # main.py
from flask import Flask, request
import telegram

app = Flask(__name__)
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
...

@app.route('/')
def hello():
    return "Bot is live"

app.run(host='0.0.0.0', port=8080)