from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from flask import Flask, request
import threading, os, json, requests
from datetime import datetime

# ========== CONFIG ==========
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "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"
DATA_FILE = "users.json"

ADS = [
    "💡 Dexmate Pro launches 16 August!",
    "🚀 Share Dexmate AI with your friends!",
    "📢 Follow @dexmateai for coding tips!"
]

# ========== FLASK + TELEGRAM ==========
flask_app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

@flask_app.route('/')
def home():
    return "✅ Dexmate AI is Live!"

@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.create_task(telegram_app.process_update(update))
    return "ok"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# ========== USER LOGIC ==========
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def user_count(uid):
    uid = str(uid)
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    if uid not in data:
        data[uid] = {"count": 0, "date": today, "ad_index": 0}
    if data[uid]["date"] != today:
        data[uid]["count"] = 0
        data[uid]["date"] = today
    data[uid]["count"] += 1
    save_data(data)
    return data[uid]["count"], data[uid]["ad_index"]

def update_ad(uid, index):
    data = load_data()
    uid = str(uid)
    if uid in data:
        data[uid]["ad_index"] = index
        save_data(data)

def is_premium():
    return datetime.now() >= datetime(2025, 8, 16)

# ========== AI CORE ==========
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
                    {"role": "system", "content": "You are a helpful AI assistant for coding."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ========== HANDLERS ==========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text.strip()
    count, ad_index = user_count(uid)

    if not is_premium() and count > 5:
        await update.message.reply_text("🚫 Daily limit reached. Try again tomorrow.")
        return

    if text.lower() == "start":
        keyboard = [[KeyboardButton("Python")], [KeyboardButton("Java")]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Choose your language:", reply_markup=markup)
    else:
        await update.message.reply_text("🤖 Thinking...")
        reply = ask_openrouter(text)
        await update.message.reply_text(reply)
        if count % 3 == 0:
            await update.message.reply_text(ADS[ad_index % len(ADS)])
            update_ad(uid, ad_index + 1)

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your ID: {update.message.from_user.id}")

# ========== MAIN ==========
if __name__ == "__main__":
    telegram_app.add_handler(CommandHandler("getid", get_id))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    threading.Thread(target=run_flask).start()

    telegram_app.bot.set_webhook(f"https://dexmateai.onrender.com/{BOT_TOKEN}")
    print("✅ Bot running at https://dexmateai.onrender.com")