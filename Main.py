from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
)
import os

# === Your Telegram Bot Info ===
BOT_TOKEN = "6730632652:AAHbFZAfWq-zNqFSRMHbVvktm65dQvn5z7I"
WEBHOOK_URL = "https://dexmateai.onrender.com/webhook"
# ==============================

app = Flask(__name__)

# Basic Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Dexmate AI is ready to help you code!")

# Echo Message
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

# Home Page (Optional)
@app.route('/')
def home():
    return '🤖 Dexmate AI is live!'

# Webhook Route
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    app.application.update_queue.put_nowait(update)
    return 'OK'

# Setup the Bot
async def run_bot():
    app.application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.application.add_handler(CommandHandler('start', start))
    app.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Set the webhook
    await app.application.bot.set_webhook(url=WEBHOOK_URL)
    app.bot = app.application.bot
    print("✅ Dexmate AI bot is running with webhook!")

if __name__ == '__main__':
    import asyncio
    asyncio.run(run_bot())
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))