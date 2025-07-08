import logging
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Bot Token
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
WEBHOOK_URL = "https://dexmateai.onrender.com/" + BOT_TOKEN

# Flask app
app = Flask(__name__)

# Telegram bot app
bot_app = Application.builder().token(BOT_TOKEN).build()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I’m Dexmate AI. Ask me anything!")

# Respond to any message (not just 'hello')
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"🔁 You said: {text}")

# Register handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask route for Telegram webhook
@app.route("/" + BOT_TOKEN, methods=["POST"])
def receive_update():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put_nowait(update)
    return "ok"

# Webhook setup
async def setup_webhook():
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    logger.info("✅ Webhook set. Bot is ready!")

# Start Flask and bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_webhook())
    logger.info("✅ Bot is Live on Render!")
    app.run(host="0.0.0.0", port=10000)