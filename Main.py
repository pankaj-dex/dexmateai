# Dexmate AI - Free Mode (Until 16 August 2025)
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from flask import Flask, request
import threading, os, json, requests
from datetime import datetime

# === FILLED API KEYS ===
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "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"

app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

@app.route('/')
def home():
    return "✅ Dexmate AI is live!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def receive_update():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.create_task(application.process_update(update))
    return "ok"

def ask_openrouter(prompt):
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "mistralai/mixtral-8x7b-instruct",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🧠 Thinking...")
    answer = ask_openrouter(text)
    await update.message.reply_text(answer)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Python")], [KeyboardButton("C++")]]
    await update.message.reply_text("Choose your language:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    application.run_polling()