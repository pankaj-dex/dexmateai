import logging
import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Your bot token
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
WEBHOOK_URL = f"https://dexmateai.onrender.com/{BOT_TOKEN}"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Create Telegram bot application
bot_app = Application.builder().token(BOT_TOKEN).build()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I’m Dexmate AI 🤖. How can I help you today?")

# Text message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    await update.message.reply_text(f"You said: {user_msg}")

# Set handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive_update():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.run(bot_app.initialize())  # REQUIRED
    asyncio.run(bot_app.process_update(update))
    return "OK"

# Root endpoint for health check
@app.route("/", methods=["GET", "HEAD"])
def index():
    return "Dexmate AI bot is running!", 200

# Start webhook on launch
async def set_webhook():
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook set. Bot is ready!")

if __name__ == "__main__":
    # Set webhook before running Flask
    asyncio.run(set_webhook())
    print("✅ Bot is Live on Render!")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))