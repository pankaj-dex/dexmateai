import logging
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your real bot token
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
WEBHOOK_URL = "https://dexmateai.onrender.com/" + BOT_TOKEN

# Flask App
app = Flask(__name__)

# Telegram Bot App
bot_app = Application.builder().token(BOT_TOKEN).build()

# Reply handler
async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I’m Dexmate AI. How can I help you?")

# Register handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))

# Webhook endpoint
@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put_nowait(update)
    return "ok"

# Start webhook setup
async def run_bot():
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    logger.info("✅ Webhook set. Bot is ready!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())
    logger.info("✅ Bot is Live on Render!")
    app.run(host="0.0.0.0", port=10000)